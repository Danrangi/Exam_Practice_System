from flask import Flask, render_template, request, redirect, url_for, session, flash, g 
from flask_sqlalchemy import SQLAlchemy

# --- 1. APP AND DATABASE CONFIGURATION ---
app = Flask(__name__)

# Configure the SQLite database, stored in the file 'exam_data.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)

# app.py (Insert this after database configuration)

# --- ADMIN CREDENTIALS ---
# CHANGE THIS TO A SECURE PASSWORD BEFORE FINAL DEPLOYMENT!
app.config['ADMIN_USERNAME'] = 'EPS' 
app.config['ADMIN_PASSWORD'] = 'AdminEPS123' 
app.config['SECRET_KEY'] = 'Danrangi@2025' # Flask needs this for session management

# --- 2. DEFINE DATABASE MODELS (SCHEMA) ---
# app.py (Insert this code block)
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

# --- 3. ROUTES (WEB PAGES) ---

# app.py (Replace the simple @app.route('/') index function with this)

@app.before_request
def before_request():
    """Sets the global variable 'g.user' to the logged-in username."""
    g.user = None
    if 'username' in session:
        g.user = session['username']

# --- ROUTES (WEB PAGES) ---

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
    # This block ensures the tables are created if they don't exist yet.
    with app.app_context():
        db.create_all()
        print("Database tables created successfully (if they didn't exist).")

    # The Codespace environment usually runs on a specific port, often 5000.
    # Host='0.0.0.0' makes it externally accessible for testing.
    app.run(debug=True, host='0.0.0.0', port=5000)
