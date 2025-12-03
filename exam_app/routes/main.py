from flask import Blueprint, render_template, request, redirect, url_for, flash, g, session
from exam_app import db
from exam_app.models import Exam, Subject, Question

main_bp = Blueprint('main', __name__)


@main_bp.route('/take_exam/<int:subject_id>', methods=['GET', 'POST'], endpoint='take_exam')
def take_exam(subject_id):
    """Handles the display of questions and submission of the exam."""
    if not g.user:
        flash('Please login to take an exam.', 'warning')
        return redirect(url_for('login'))

    subject = Subject.query.get_or_404(subject_id)
    questions = Question.query.filter_by(subject_id=subject_id).all()

    if not questions:
        flash(f"No questions available for {subject.name}.", 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        score = 0
        total_questions = len(questions)
        results = []

        for question in questions:
            user_answer = request.form.get(f'q_{question.id}')
            is_correct = (user_answer == question.correct_answer)

            results.append({
                'id': question.id,
                'question_text': question.question_text,
                'user_answer': user_answer,
                'correct_answer': question.correct_answer,
                'is_correct': is_correct,
                'explanation': question.explanation,
                'options': {
                    'A': question.option_a,
                    'B': question.option_b,
                    'C': question.option_c,
                    'D': question.option_d,
                }
            })

            if is_correct:
                score += 1

        session['last_exam_results'] = {
            'subject_name': subject.name,
            'score': score,
            'total_questions': total_questions,
            'results_list': results
        }

        return redirect(url_for('exam_results'))

    return render_template('take_exam.html', subject=subject, questions=questions)


@main_bp.route('/exam_results', endpoint='exam_results')
def exam_results():
    if not g.user:
        return redirect(url_for('login'))

    results = session.pop('last_exam_results', None)

    if not results:
        flash("No recent exam results found.", 'info')
        return redirect(url_for('dashboard'))

    return render_template('exam_results.html', results=results)


@main_bp.route('/dashboard', endpoint='dashboard')
def dashboard():
    if not g.user:
        flash('Please login to access this page.', 'warning')
        return redirect(url_for('login'))

    exams = Exam.query.all()

    return render_template('dashboard.html', exams=exams)
