from flask import Flask, render_template, jsonify, request, send_from_directory
import json
import os

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

# Helper function to read data from JSON file
def read_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
        # Ensure all groups have a display_type, default to 'normal'
        for group in data:
            if 'display_type' not in group:
                group['display_type'] = 'normal'
        return data

# Helper function to write data to JSON file
def write_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Helper function to get a group by name
def get_group_by_name(groups, group_name):
    for group in groups:
        if group['name'] == group_name:
            return group
    return None

@app.route('/')
def index():
    return render_template('myhome_input.html')

@app.route('/myhome/<path:filename>')
def serve_myhome_static(filename):
    return send_from_directory('myhome', filename)

@app.route('/api/groups', methods=['GET'])
def get_groups():
    groups = read_data()
    return jsonify(groups)

@app.route('/api/links', methods=['GET'])
def get_links():
    groups = read_data()
    all_links = []
    for group in groups:
        for link in group.get('links', []):
            all_links.append(link)
    return jsonify(all_links)

@app.route('/api/links', methods=['PUT'])
def update_all_links():
    new_links_flat = request.json
    groups = read_data()

    # Reconstruct groups from the flat list of links
    updated_groups = {}
    for link in new_links_flat:
        group_name = link.get('group', 'Ungrouped')
        if group_name not in updated_groups:
            # Preserve existing display_type if group already exists, otherwise default to 'normal'
            existing_group = get_group_by_name(groups, group_name)
            updated_groups[group_name] = {
                'name': group_name,
                'display_type': existing_group['display_type'] if existing_group else 'normal',
                'links': []
            }
        updated_groups[group_name]['links'].append(link)
    
    # Maintain the order of existing groups and add new ones at the end
    final_groups = []
    existing_group_names = [g['name'] for g in groups]
    for group_name in existing_group_names:
        if group_name in updated_groups:
            final_groups.append(updated_groups.pop(group_name))
    
    # Add any new groups
    for group_name in updated_groups:
        final_groups.append(updated_groups[group_name])

    write_data(final_groups)
    return jsonify({'message': 'Links updated successfully'})

@app.route('/api/groups', methods=['PUT'])
def update_all_groups():
    new_groups = request.json
    write_data(new_groups)
    return jsonify({'message': 'Groups order updated successfully'})

@app.route('/api/add_link', methods=['POST'])
def add_link():
    new_link = request.json
    if 'default_type' not in new_link or not new_link['default_type']:
        new_link['default_type'] = 'nerd-font'
    
    groups = read_data()
    group_name = new_link.get('group', 'Ungrouped')
    
    target_group = get_group_by_name(groups, group_name)
    if not target_group:
        target_group = {'name': group_name, 'display_type': 'normal', 'links': []}
        groups.append(target_group)
    
    target_group['links'].append(new_link)
    write_data(groups)
    return jsonify({'message': 'Link added successfully'}), 201

@app.route('/api/links/<int:link_id>', methods=['PUT'])
def edit_link(link_id):
    updated_link = request.json
    if 'default_type' not in updated_link or not updated_link['default_type']:
        updated_link['default_type'] = 'nerd-font'
    
    groups = read_data()
    current_link_index = 0
    for group in groups:
        for i, link in enumerate(group.get('links', [])):
            if current_link_index == link_id:
                # Check if group name changed
                old_group_name = link.get('group', 'Ungrouped')
                new_group_name = updated_link.get('group', 'Ungrouped')

                if old_group_name == new_group_name:
                    # Same group, just update the link
                    group['links'][i] = updated_link
                else:
                    # Group changed, move the link
                    group['links'].pop(i)
                    target_group = get_group_by_name(groups, new_group_name)
                    if not target_group:
                        target_group = {'name': new_group_name, 'display_type': 'normal', 'links': []}
                        groups.append(target_group)
                    target_group['links'].append(updated_link)
                write_data(groups)
                return jsonify({'message': 'Link updated successfully'})
            current_link_index += 1
    return jsonify({'message': 'Link not found'}), 404

@app.route('/api/links/<int:link_id>', methods=['DELETE'])
def delete_link(link_id):
    groups = read_data()
    current_link_index = 0
    for group in groups:
        for i, link in enumerate(group.get('links', [])):
            if current_link_index == link_id:
                deleted_link = group['links'].pop(i)
                # If group becomes empty, remove it
                if not group['links'] and group['name'] != 'Ungrouped':
                    groups.remove(group)
                write_data(groups)
                return jsonify({'message': 'Link deleted successfully', 'deleted_link': deleted_link})
            current_link_index += 1
    return jsonify({'message': 'Link not found'}), 404

@app.route('/api/groups/<group_name>', methods=['PUT'])
def update_group(group_name):
    updated_group_data = request.json
    groups = read_data()
    
    target_group = get_group_by_name(groups, group_name)
    if target_group:
        # Update group name if provided and different
        if 'new_name' in updated_group_data and updated_group_data['new_name'] != group_name:
            # Check if new name already exists
            if get_group_by_name(groups, updated_group_data['new_name']):
                return jsonify({'message': 'Group with new name already exists'}), 409
            target_group['name'] = updated_group_data['new_name']
            # Update group name in all links belonging to this group
            for link in target_group['links']:
                link['group'] = updated_group_data['new_name']
        
        # Update display_type if provided
        if 'display_type' in updated_group_data:
            target_group['display_type'] = updated_group_data['display_type']
            
        write_data(groups)
        return jsonify({'message': 'Group updated successfully'})
    return jsonify({'message': 'Group not found'}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

