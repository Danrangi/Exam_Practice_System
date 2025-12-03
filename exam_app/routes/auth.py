from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g, current_app

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/', methods=['GET', 'POST'], endpoint='login')
def login():
    if g.user:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Admin login
        if username == current_app.config['ADMIN_USERNAME'] and password == current_app.config['ADMIN_PASSWORD']:
            session['username'] = username
            flash('Admin Login successful! You have full access.', 'success')
            return redirect(url_for('dashboard'))
        # Any non-admin credentials allowed as a "student" login
        elif username and password:
            session['username'] = username
            flash(f'Welcome, {username}! Start your practice.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials or fields missing. Please try again.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout', endpoint='logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))
