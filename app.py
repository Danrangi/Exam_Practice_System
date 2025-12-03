from flask import Flask, render_template, request, redirect, url_for, session, flash, g 
from flask_sqlalchemy import SQLAlchemy

"""Minimal runner that creates the app using the application factory."""

from exam_app import create_app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
if __name__ == '__main__':
    # We need to create the database tables *before* running the app.
    with app.app_context():
        db.create_all()
        # Call the function to populate initial data
        add_initial_data() 
        print("Database tables created successfully (if they didn't exist).")

    app.run(debug=True, host='0.0.0.0', port=5000)