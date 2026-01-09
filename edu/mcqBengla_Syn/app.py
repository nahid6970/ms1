from flask import Flask, render_template, request, jsonify
import json
import random

app = Flask(__name__)

# Load questions data
with open('questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def generate_quiz(num_questions=10):
    """Generate a random quiz with specified number of questions"""
    quiz_questions = []
    synonym_groups = data['synonym_groups']
    
    # Get all words for random options
    all_words = []
    for group in synonym_groups:
        all_words.extend(group['words'])
    
    for _ in range(num_questions):
        # Select a random group
        selected_group = random.choice(synonym_groups)
        group_words = selected_group['words']
        
        # Skip if group has less than 2 words
        if len(group_words) < 2:
            continue
            
        # Select question word and correct answer
        question_word = random.choice(group_words)
        remaining_words = [w for w in group_words if w != question_word]
        correct_answer = random.choice(remaining_words)
        
        # Generate 3 random wrong options from other groups
        wrong_options = []
        available_words = [w for w in all_words if w not in group_words]
        
        while len(wrong_options) < 3 and available_words:
            wrong_word = random.choice(available_words)
            if wrong_word not in wrong_options:
                wrong_options.append(wrong_word)
                available_words.remove(wrong_word)
        
        # Create options list and shuffle
        options = [correct_answer] + wrong_options
        random.shuffle(options)
        
        # Find correct answer index
        correct_index = options.index(correct_answer)
        
        quiz_questions.append({
            'question': f"{question_word} এর সমার্থক",
            'options': options,
            'correct': correct_index,
            'group': selected_group['group']
        })
    
    return quiz_questions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate-quiz')
def api_generate_quiz():
    num_questions = request.args.get('num_questions', 10, type=int)
    quiz = generate_quiz(num_questions)
    return jsonify(quiz)

@app.route('/api/check-answer', methods=['POST'])
def check_answer():
    data = request.json
    question_index = data.get('question_index')
    selected_option = data.get('selected_option')
    correct_answer = data.get('correct_answer')
    
    is_correct = selected_option == correct_answer
    
    return jsonify({
        'correct': is_correct,
        'message': 'সঠিক!' if is_correct else 'ভুল!'
    })

if __name__ == '__main__':
    app.run(debug=True, port=4421)