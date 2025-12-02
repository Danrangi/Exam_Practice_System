from flask import Flask, render_template, request, redirect, url_for, session, flash, g 
from flask_sqlalchemy import SQLAlchemy

# --- 1. APP AND DATABASE CONFIGURATION ---
app = Flask(__name__)

# Configure the SQLite database, stored in the file 'exam_data.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)

# --- ADMIN CREDENTIALS ---
# CHANGE THIS TO A SECURE PASSWORD BEFORE FINAL DEPLOYMENT!
app.config['ADMIN_USERNAME'] = 'EPS' 
app.config['ADMIN_PASSWORD'] = 'AdminEPS123' 
app.config['SECRET_KEY'] = 'Danrangi@2025' # Flask needs this for session management

# --- 2. DEFINE DATABASE MODELS (SCHEMA) ---

# Model 1: Exam Type (e.g., JAMB, WAEC, NECO)
class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # e.g., 'JAMB'
    description = db.Column(db.String(200))
    # Relationship: One Exam can have multiple Subjects
    subjects = db.relationship('Subject', backref='exam', lazy=True)

# Model 2: Subject (e.g., English, Mathematics, Physics)
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False) # e.g., 'English Language'
    # Foreign Key linking Subject back to Exam
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    # Relationship: One Subject can have multiple Questions
    questions = db.relationship('Question', backref='subject', lazy=True)
    # Ensures a subject name is unique within a specific exam (e.g., 'Physics' for JAMB is different from 'Physics' for WAEC)
    __table_args__ = (db.UniqueConstraint('name', 'exam_id', name='_name_exam_uc'),)

# Model 3: Question
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    # Options (we will store them simply as strings)
    option_a = db.Column(db.String(500), nullable=False)
    option_b = db.Column(db.String(500), nullable=False)
    option_c = db.Column(db.String(500), nullable=False)
    option_d = db.Column(db.String(500), nullable=False)
    # The correct answer must be one of the options (A, B, C, or D)
    correct_answer = db.Column(db.String(1), nullable=False)
    # Foreign Key linking Question back to Subject
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    # Optional field for the admin to add an explanation
    explanation = db.Column(db.Text)


def add_initial_data():
    """Adds the three main exam types if they do not already exist."""
    
    # Check if JAMB exists
    if not Exam.query.filter_by(name='JAMB').first():
        jamb = Exam(name='JAMB', description='Joint Admissions and Matriculation Board')
        db.session.add(jamb)
    
    # Check if WAEC exists
    if not Exam.query.filter_by(name='WAEC').first():
        waec = Exam(name='WAEC', description='West African Examinations Council')
        db.session.add(waec)
        
    # Check if NECO exists
    if not Exam.query.filter_by(name='NECO').first():
        neco = Exam(name='NECO', description='National Examination Council')
        db.session.add(neco)
        
    # Commit all changes to the database
    db.session.commit()
    print("Initial exam data checked and added if missing.")

# --- 3. ROUTES (WEB PAGES) ---

@app.before_request
def before_request():
    """Sets the global variable 'g.user' to the logged-in username."""
    g.user = None
    if 'username' in session:
        g.user = session['username']

@app.route('/', methods=['GET', 'POST'])
def login():
    if g.user:
        # If user is already logged in, redirect them to the dashboard
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    
    # Render the login form
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# >>> MISSING ROUTE INSERTED HERE (The fix for the BuildError) <<<
# app.py (REPLACE the existing admin_panel function with this)

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    """Handles displaying exam/subject data and creating new subjects."""
    if not g.user:
        flash('Please login to access the admin panel.', 'warning')
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        exam_id = request.form.get('exam_id')
        subject_name = request.form.get('subject_name', '').strip()

        if not exam_id or not subject_name:
            flash('Both Exam Type and Subject Name are required.', 'danger')
        else:
            try:
                # Check for uniqueness first (SQLAlchemy handles this too, but this gives a cleaner error message)
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

    # Data to display on the page (always executed on GET and after POST)
    exams = Exam.query.all()
    # Fetch all subjects to display under their respective exams
    all_subjects = Subject.query.order_by(Subject.exam_id, Subject.name).all()
    
    # Organize subjects by exam ID for easier rendering in the template
    subjects_by_exam = {}
    for exam in exams:
        subjects_by_exam[exam.id] = []
    for subject in all_subjects:
        subjects_by_exam[subject.exam_id].append(subject)

    return render_template('admin_panel.html', exams=exams, subjects_by_exam=subjects_by_exam)# >>> END OF MISSING ROUTE <<<

# app.py (Insert this new route after the existing admin_panel function)

@app.route('/admin/questions/<int:subject_id>', methods=['GET', 'POST'])
def question_management(subject_id):
    """Handles CRUD operations for Questions related to a specific Subject."""
    if not g.user:
        flash('Please login to access question management.', 'warning')
        return redirect(url_for('login'))

    subject = Subject.query.get_or_404(subject_id)
    exam = subject.exam # Automatically loaded via backref

    if request.method == 'POST':
        # Retrieve form data
        question_text = request.form.get('question_text', '').strip()
        option_a = request.form.get('option_a', '').strip()
        option_b = request.form.get('option_b', '').strip()
        option_c = request.form.get('option_c', '').strip()
        option_d = request.form.get('option_d', '').strip()
        correct_answer = request.form.get('correct_answer', '').upper()
        explanation = request.form.get('explanation', '').strip()

        # Simple validation
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
                # Redirect to GET request to clear the form
                return redirect(url_for('question_management', subject_id=subject_id))

            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred while adding the question: {e}", 'danger')

    # Data for GET (and after POST redirect)
    questions = Question.query.filter_by(subject_id=subject_id).order_by(Question.id.desc()).all()
    
    return render_template(
        'question_management.html', 
        subject=subject, 
        exam=exam, 
        questions=questions
    )

@app.route('/dashboard')
def dashboard():
    """Placeholder dashboard."""
    if not g.user:
        flash('Please login to access this page.', 'warning')
        return redirect(url_for('login'))
        
    return render_template('dashboard.html')

# --- 4. MAIN APPLICATION RUNNER ---

if __name__ == '__main__':
    # We need to create the database tables *before* running the app.
    with app.app_context():
        db.create_all()
        # NEW LINE: Call the function to populate initial data
        add_initial_data() 
        print("Database tables created successfully (if they didn't exist).")

    app.run(debug=True, host='0.0.0.0', port=5000)