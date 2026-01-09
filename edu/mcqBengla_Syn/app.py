from flask import Flask, render_template, request, jsonify
import json
import random
from datetime import datetime
import os

app = Flask(__name__)

# Load questions data
with open('questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# History file path
HISTORY_FILE = 'quiz_history.json'

def load_history():
    """Load quiz history from file"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    """Save quiz history to file"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

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

@app.route('/api/save-quiz-result', methods=['POST'])
def save_quiz_result():
    """Save quiz result to history"""
    data = request.json
    
    history = load_history()
    
    # Create quiz result entry
    quiz_result = {
        'id': len(history) + 1,
        'date': datetime.now().isoformat(),
        'total_questions': data.get('total_questions'),
        'correct_answers': data.get('correct_answers'),
        'score_percentage': data.get('score_percentage'),
        'time_taken': data.get('time_taken', 0),
        'categories_performance': data.get('categories_performance', {}),
        'difficulty': data.get('difficulty', 'মিশ্র')
    }
    
    history.append(quiz_result)
    save_history(history)
    
    return jsonify({'success': True, 'quiz_id': quiz_result['id']})

@app.route('/api/get-history')
def get_history():
    """Get quiz history and analytics"""
    history = load_history()
    
    if not history:
        return jsonify({
            'history': [],
            'analytics': {
                'total_quizzes': 0,
                'average_score': 0,
                'best_score': 0,
                'total_questions_answered': 0,
                'improvement_trend': 'নেই'
            }
        })
    
    # Calculate analytics
    total_quizzes = len(history)
    scores = [quiz['score_percentage'] for quiz in history]
    average_score = sum(scores) / len(scores)
    best_score = max(scores)
    total_questions = sum(quiz['total_questions'] for quiz in history)
    
    # Calculate improvement trend (last 5 vs previous 5)
    improvement_trend = 'স্থিতিশীল'
    if len(history) >= 10:
        recent_avg = sum(scores[-5:]) / 5
        previous_avg = sum(scores[-10:-5]) / 5
        if recent_avg > previous_avg + 5:
            improvement_trend = 'উন্নতি'
        elif recent_avg < previous_avg - 5:
            improvement_trend = 'অবনতি'
    
    analytics = {
        'total_quizzes': total_quizzes,
        'average_score': round(average_score, 1),
        'best_score': best_score,
        'total_questions_answered': total_questions,
        'improvement_trend': improvement_trend,
        'recent_scores': scores[-10:] if len(scores) >= 10 else scores
    }
    
    return jsonify({
        'history': history[-20:],  # Last 20 quizzes
        'analytics': analytics
    })

@app.route('/api/get-weak-areas')
def get_weak_areas():
    """Analyze weak areas based on quiz history"""
    history = load_history()
    
    if not history:
        return jsonify({'weak_areas': [], 'suggestions': []})
    
    # Analyze category performance
    category_stats = {}
    for quiz in history:
        for category, performance in quiz.get('categories_performance', {}).items():
            if category not in category_stats:
                category_stats[category] = {'correct': 0, 'total': 0}
            category_stats[category]['correct'] += performance.get('correct', 0)
            category_stats[category]['total'] += performance.get('total', 0)
    
    # Find weak areas (less than 60% accuracy)
    weak_areas = []
    for category, stats in category_stats.items():
        if stats['total'] > 0:
            accuracy = (stats['correct'] / stats['total']) * 100
            if accuracy < 60:
                weak_areas.append({
                    'category': category,
                    'accuracy': round(accuracy, 1),
                    'questions_attempted': stats['total']
                })
    
    # Sort by lowest accuracy
    weak_areas.sort(key=lambda x: x['accuracy'])
    
    # Generate suggestions
    suggestions = []
    if weak_areas:
        suggestions.append(f"'{weak_areas[0]['category']}' বিষয়ে বেশি অনুশীলন করুন")
        suggestions.append("কঠিন শব্দগুলো নোট করে রাখুন")
        suggestions.append("প্রতিদিন ১০-১৫টি প্রশ্নের অনুশীলন করুন")
    else:
        suggestions.append("চমৎকার! সব বিষয়ে ভালো দক্ষতা রয়েছে")
        suggestions.append("নিয়মিত অনুশীলন চালিয়ে যান")
    
    return jsonify({
        'weak_areas': weak_areas[:5],  # Top 5 weak areas
        'suggestions': suggestions
    })

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