from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g, current_app as app
from exam_app import db
from exam_app.models import Exam, Subject, Question
from sqlalchemy import select

# Define the blueprint
bp = Blueprint('main', __name__)

@bp.route('/dashboard')
def dashboard():
    """Student dashboard showing available exams and subjects."""
    if not g.user:
        flash('Please login to access this page.', 'warning')
        return redirect(url_for('auth.login'))
        
    # Fetch all exams
    exams = db.session.execute(db.select(Exam)).scalars().all()
    
    # FIX: Use 'current_app as app' to access config variables
    admin_username = app.config['ADMIN_USERNAME']
        
    return render_template('dashboard.html', exams=exams, admin_username=admin_username)


@bp.route('/take_exam/<int:subject_id>', methods=['GET', 'POST'])
def take_exam(subject_id):
    """Handles the display of questions and submission of the exam."""
    if not g.user:
        flash('Please login to take an exam.', 'warning')
        return redirect(url_for('auth.login'))

    subject = db.session.execute(db.select(Subject).filter_by(id=subject_id)).scalar_one_or_none()
    if not subject:
        flash("Subject not found.", 'danger')
        return redirect(url_for('main.dashboard'))
        
    questions = db.session.execute(db.select(Question).filter_by(subject_id=subject_id)).scalars().all()

    if not questions:
        flash(f"No questions available for {subject.name}.", 'danger')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        # Score calculation and result handling
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
        
        return redirect(url_for('main.exam_results'))

    # GET request: Display the exam questions
    return render_template(
        'take_exam.html', 
        subject=subject, 
        questions=questions
    )


@bp.route('/exam_results')
def exam_results():
    """Displays the results of the last completed exam."""
    if not g.user:
        return redirect(url_for('auth.login'))

    results = session.pop('last_exam_results', None)
    
    if not results:
        flash("No recent exam results found.", 'info')
        return redirect(url_for('main.dashboard'))
        
    return render_template('exam_results.html', results=results)