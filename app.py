# app.py
from models import Tutor, SchoolType, Subject, TutorSubject, Student, Lesson
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, logging, flash
from functools import wraps
from models import db, SchoolType, Student, Users # ... import other classes as needed
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from funcs import *
from flask_migrate import Migrate



app = Flask(__name__)
# Database configuration and initialization
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:rootroot@localhost/showcase'
app.config['SECRET_KEY'] = 'development'
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)

bcrypt = Bcrypt(app)

with app.app_context():
    db.create_all()



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/tutors')
def list_tutors():
    tutors = Tutor.query.all()
    return '<br>'.join([tutor.name for tutor in tutors])

@app.route('/lessons', methods=['GET', 'POST'])
def create_lesson():
    if request.method == 'POST':
        if 'tutor' in request.form and 'student_id' in request.form and 'subject' in request.form:
            tutor_id = int(request.form['tutor'])
            student_id = int(request.form['student_id'])
            subject_id = int(request.form['subject'])
            date = request.form['date']
            start_time = request.form['start_time']
            end_time = request.form['end_time']

            # Create a new lesson instance
            new_lesson = Lesson(tutor_id=tutor_id, student_id=student_id, subject_id=subject_id, 
                                date=date, start_time=start_time, end_time=end_time)

            # Add to the database
            db.session.add(new_lesson)
            db.session.commit()

            # Redirect to the same page (or another page if you prefer)
            return redirect(url_for('create_lesson'))
        elif 'new_student' in request.form:
            return redirect(url_for('create_student'))  
    return render_template('create_lesson.html')



@app.route('/api/schooltypes')
def get_schooltypes():
    schooltypes = SchoolType.query.all()
    return jsonify([{'id': st.schooltype_id, 'name': st.schooltype_name} for st in schooltypes])

@app.route('/api/subjects/<int:schooltype_id>')
def get_subjects(schooltype_id):
    subjects = Subject.query.filter_by(schooltype_id=schooltype_id).all()
    return jsonify([{'id': s.subject_id, 'name': s.subject_name} for s in subjects])

@app.route('/get_tutors/<int:subject_id>', methods=['GET'])
def get_tutors(subject_id):
    tutors = db.session.query(Tutor).join(TutorSubject).filter(TutorSubject.subject_id == subject_id).all()
    return jsonify([{'id': tutor.tutor_id, 'name': tutor.name} for tutor in tutors])

@app.route('/api/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    students_data = [{'id': student.StudentID, 'name': f'{student.FirstName} {student.LastName}'} for student in students]
    return jsonify(students_data)

@app.route('/api/students/<int:schooltype_id>/<int:subject_id>')
def get_students_for_subject(schooltype_id, subject_id):
    # Query the students associated with the selected school and subject
    students = Student.query.filter_by(schooltype_id=schooltype_id, subject_id=subject_id).all()
    students_data = [{'id': student.StudentID, 'name': f'{student.FirstName} {student.LastName}'} for student in students]
    return jsonify(students_data)

@app.route('/new_student', methods=['GET'])
def new_student_form():
    return render_template('create_student.html')  # This template should contain a form to create a new student

@app.route('/create_student', methods=['POST'])
def create_student():
    if request.method == 'POST':
        # Retrieve and validate student information from the form
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        # Add other student information fields

        # Create a new student instance
        new_student = Student(first_name=first_name, last_name=last_name)
        # Set other student information fields

        # Add the new student to the database
        db.session.add(new_student)
        db.session.commit()

        # Redirect to the page where you want to use the newly created student
        return redirect(url_for('create_lesson'))


@app.route('/api/students', methods=['POST'])
def create_student_api():
    first_name = request.form['new_student_first_name']
    last_name = request.form['new_student_last_name']
    # Retrieve and process other student-related fields as needed

    # Create a new student instance
    new_student = Student(FirstName=first_name, LastName=last_name)
    # Set other student attributes based on the form data

    # Add to the database
    db.session.add(new_student)
    db.session.commit()

    # Redirect to the same page (or another page if you prefer)
    return redirect(url_for('create_lesson'))

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve username and password from the form
        username = request.form['username']
        password = request.form['password']

        # Query the database for the user
        user = Users.query.filter_by(username=username).first()

        # Check if the user exists and the password is correct
        if user and user.check_password(password):
            # Log in the user
            login_user(user)
            flash('Logged in successfully.')
            # Redirect to the page the user tried to access
            return redirect(request.args.get('next') or url_for('index'))
        else:
            # Redirect to the login page if the login failed
            flash('Invalid username or password')
            return redirect(url_for('login'))
    else:
        return render_template('login.html')
    
@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash("You don't have permission to access this page.")
        return(url_for('index'))
    return render_template('admin_dashboard.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
