from flask import Blueprint, render_template, request, redirect, url_for, flash, g, current_app
from exam_app import db
from exam_app.models import Exam, Subject, Question

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('', methods=['GET', 'POST'], endpoint='admin_panel')
def admin_panel():
    """
    Handles displaying exam/subject data and creating new subjects.
    REQUIRES: Logged in user must be the Admin.
    """
    admin_username = current_app.config['ADMIN_USERNAME']

    # --- ADDED ADMIN AUTHORIZATION CHECK ---
    if g.user != admin_username:
        flash('Authorization required. You must be the administrator to access this panel.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        exam_id = request.form.get('exam_id')
        subject_name = request.form.get('subject_name', '').strip()

        if not exam_id or not subject_name:
            flash('Both Exam Type and Subject Name are required.', 'danger')
        else:
            try:
                existing_subject = Subject.query.filter_by(name=subject_name, exam_id=exam_id).first()
                if existing_subject:
                    exam_name = Exam.query.get(exam_id).name
                    flash(f"Subject '{subject_name}' already exists for {exam_name}.", 'danger')
                else:
                    new_subject = Subject(name=subject_name, exam_id=exam_id)
                    db.session.add(new_subject)
                    db.session.commit()
                    flash(f"Subject '{subject_name}' added successfully!", 'success')
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred while adding the subject: {e}", 'danger')

    exams = Exam.query.all()
    all_subjects = Subject.query.order_by(Subject.exam_id, Subject.name).all()

    subjects_by_exam = {}
    for exam in exams:
        subjects_by_exam[exam.id] = [s for s in all_subjects if s.exam_id == exam.id]

    return render_template(
        'admin_panel.html',
        exams=exams,
        subjects_by_exam=subjects_by_exam
    )


@admin_bp.route('/questions/<int:subject_id>', methods=['GET', 'POST'], endpoint='question_management')
def question_management(subject_id):
    """
    Handles CRUD operations for Questions related to a specific Subject.
    REQUIRES: Logged in user must be the Admin.
    """
    admin_username = current_app.config['ADMIN_USERNAME']

    # --- ADDED ADMIN AUTHORIZATION CHECK ---
    if g.user != admin_username:
        flash('Authorization required. You must be the administrator to access this panel.', 'danger')
        return redirect(url_for('dashboard'))

    subject = Subject.query.get_or_404(subject_id)
    exam = subject.exam

    if request.method == 'POST':
        question_text = request.form.get('question_text', '').strip()
        option_a = request.form.get('option_a', '').strip()
        option_b = request.form.get('option_b', '').strip()
        option_c = request.form.get('option_c', '').strip()
        option_d = request.form.get('option_d', '').strip()
        correct_answer = request.form.get('correct_answer', '').upper()
        explanation = request.form.get('explanation', '').strip()

        if not all([question_text, option_a, option_b, option_c, option_d, correct_answer]):
            flash('All question fields and the correct answer must be provided.', 'danger')
        elif correct_answer not in ['A', 'B', 'C', 'D']:
            flash('Correct answer must be A, B, C, or D.', 'danger')
        else:
            try:
                new_question = Question(
                    question_text=question_text,
                    option_a=option_a,
                    option_b=option_b,
                    option_c=option_c,
                    option_d=option_d,
                    correct_answer=correct_answer,
                    explanation=explanation,
                    subject_id=subject_id
                )
                db.session.add(new_question)
                db.session.commit()
                flash('Question added successfully!', 'success')
                return redirect(url_for('question_management', subject_id=subject_id))
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred while adding the question: {e}", 'danger')

    questions = Question.query.filter_by(subject_id=subject_id).order_by(Question.id.desc()).all()

    return render_template('question_management.html', subject=subject, exam=exam, questions=questions)
