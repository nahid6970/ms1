from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///c:/msBackups/DataBase/quiz.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Question model
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    answer_a = db.Column(db.String(100), nullable=False)
    answer_b = db.Column(db.String(100), nullable=False)
    answer_c = db.Column(db.String(100), nullable=False)
    answer_d = db.Column(db.String(100), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)  # A, B, C, or D
    correct_count = db.Column(db.Integer, default=0)  # Track correct answers
    incorrect_count = db.Column(db.Integer, default=0)  # Track incorrect answers


@app.route('/')
def home():
    questions = Question.query.all()
    # Sort questions by success rate
    def success_rate(q):
        total = q.correct_count + q.incorrect_count
        return q.correct_count / total if total > 0 else 0
    questions = sorted(questions, key=success_rate)
    question_count = len(questions)  # <-- COUNT questions
    return render_template('index.html', questions=questions, question_count=question_count)



@app.route('/add', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        question_text = request.form['question']
        answer_a = request.form['answer_a']
        answer_b = request.form['answer_b']
        answer_c = request.form['answer_c']
        answer_d = request.form['answer_d']
        correct_answer = request.form['correct_answer']
        new_question = Question(question=question_text, answer_a=answer_a,
                                answer_b=answer_b, answer_c=answer_c,
                                answer_d=answer_d, correct_answer=correct_answer)
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for('home'))    
    return render_template('add_question.html')


@app.route("/quiz")
def quiz():
    all_questions = Question.query.all()
    selected_questions = random.sample(all_questions, min(2, len(all_questions)))

    shuffled_questions = []
    for q in selected_questions:
        options = [
            ("A", q.answer_a),
            ("B", q.answer_b),
            ("C", q.answer_c),
            ("D", q.answer_d)
        ]
        random.shuffle(options)
        shuffled_questions.append({
            "question": q,
            "answers": options,
            "correct_count": q.correct_count or 0,
            "incorrect_count": q.incorrect_count or 0
        })
    
    selected_ids = [q.id for q in selected_questions]  # <- Add this line

    return render_template("quiz.html", shuffled_questions=shuffled_questions, selected_ids=selected_ids)


@app.route('/submit', methods=['POST'])
def submit_quiz():
    question_ids = request.form.getlist('question_ids')  # ✅ only selected IDs
    questions = Question.query.filter(Question.id.in_(question_ids)).all()

    results = []
    score = 0
    for question in questions:
        selected = request.form.get(f'answer_{question.id}')
        correct = question.correct_answer
        is_correct = selected == correct
        if is_correct:
            question.correct_count += 1
            score += 1
        else:
            question.incorrect_count += 1
        db.session.commit()

        results.append({
            'question': question.question,
            'selected': selected,
            'correct': correct,
            'answers': {
                'A': question.answer_a,
                'B': question.answer_b,
                'C': question.answer_c,
                'D': question.answer_d
            },
            'is_correct': is_correct
        })

    return render_template('result.html', score=score, total=len(questions), results=results)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_question(id):
    question = Question.query.get_or_404(id)
    if request.method == 'POST':
        question.question = request.form['question']
        question.answer_a = request.form['answer_a']
        question.answer_b = request.form['answer_b']
        question.answer_c = request.form['answer_c']
        question.answer_d = request.form['answer_d']
        question.correct_answer = request.form['correct_answer']
        db.session.commit()
        return redirect(url_for('quiz'))
    return render_template('edit_question.html', question=question)


@app.route('/delete/<int:id>')
def delete_question(id):
    question = Question.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('quiz'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5009, debug=True)

