# app.py
from models import Tutor, SchoolType, Subject, Student, Lesson
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, logging, flash
from functools import wraps
from models import db, SchoolType, Student, User, Role, Tutor, Lesson, Subject, TutorAvailability, TutorSubject, Family, Weekday, Note, lesson_students, PriceAdjustment
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from funcs import *
from flask_migrate import Migrate
from datetime import datetime, timedelta
from functools import wraps
from config import Config


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'admin':
            flash("You don't have permission to access this page.", 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def tutor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'tutor':
            flash("You don't have permission to access this page.", 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def tutor_with_id_required(f, user_id):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'tutor' or current_user.id != user_id:
            flash("You don't have permission to access this page.", 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def create_paygrade(amount):
    with app.app_context():
        paygrade = Paygrade.query.filter_by(value=amount).first()
        if not paygrade:
            paygrade = Paygrade(value=amount)
            db.session.add(paygrade)
            db.session.commit()
            print(f"Paygrade '{amount}' created.")
        else:
            print(f"Paygrade '{amount}' already exists.")

def create_price_adjustment(name, value):
    with app.app_context():
        adjustment = PriceAdjustment.query.filter_by(name=name).first()
        if not adjustment:
            adjustment = PriceAdjustment(name=name, value=value)
            db.session.add(adjustment)
            db.session.commit()
            print(f"Price adjustment '{name}' created.")
        else:
            print(f"Price adjustment '{name}' already exists.")

def create_admin_user(username, password):
    with app.app_context():
        # Ensure the admin role exists
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin')
            db.session.add(admin_role)
            db.session.commit()

        # Ensure the paygrade entry exists
        create_paygrade(1)  # Assuming '1' is the value for the default paygrade

        # Retrieve the paygrade entry
        paygrade = Paygrade.query.filter_by(value=1).first()
        if not paygrade:
            print("Failed to create or retrieve the paygrade entry.")
            return

        # Create the admin user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User.query.filter_by(username=username).first()
        if user is not None:
            print(f"User '{username}' already exists. No new user created.")
            return

        admin_user = User(username=username, password_hash=hashed_password, role_id=admin_role.id, paygrade_id=paygrade.id)
        db.session.add(admin_user)
        db.session.commit()
        print(f"Admin user '{username}' created.")

def create_role(role_name):
    with app.app_context():
        # check if the role already exists
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name)
            db.session.add(role)
            db.session.commit()
            print(f"Role '{role_name}' created.")
        else:
            print(f"Role '{role_name}' already exists.")

def create_user_with_role(username, password, role_name, paygrade=2):
    role = Role.query.filter_by(name=role_name).first()
    if role and role.name == 'admin':
        new_user = User(username=username, password_hash=bcrypt.generate_password_hash(password).decode('utf-8'), role_id=role.id, paygrade_id=1)
        db.session.add(new_user)
        db.session.commit()
        print(f"User '{username}' created with role '{role_name}'")
        return "User created successfully", True
    elif role and role.name == 'tutor':
        if paygrade is not None:
            new_user = User(username=username, password_hash=bcrypt.generate_password_hash(password).decode('utf-8'), role_id=role.id, paygrade_id=paygrade)
            db.session.add(new_user)
            db.session.commit()
            print(f"User '{username}' created with role '{role_name}'")
            return "User created successfully", True
        else:
            print("Paygrade is required for tutor role.")
            return "Paygrade is required for tutor role.", False
    else:
        print(f"Role '{role_name}' does not exist.")
        return f"Role '{role_name}' does not exist.", False

def get_schooltype_id_of_subject(subject_id):
    subject = Subject.query.get(subject_id)
    return subject.schooltype_id if subject else None

def add_weekdays():
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for day in weekdays:
        existing_day = Weekday.query.filter_by(weekday_name=day).first()
        if not existing_day:
            new_day = Weekday(weekday_name=day)
            db.session.add(new_day)
            db.session.commit()
            print(f"Weekday '{day}' created.")
        else:
            print(f"Weekday '{day}' already exists.")


def calculate_monthly_income():
    monthly_income = 0
    return monthly_income
def get_lessons_count():
    lesson_count = 0
    return lesson_count
def get_detailed_statistics():
    detailed_statistics = 0
    return detailed_statistics

from sqlalchemy import or_

def get_lessons_in_range(from_date, end_date, subject_id=None, family_id=None, tutor_id=None):
    lessons = Lesson.query.filter(Lesson.date.between(from_date, end_date))    
    
      
    if subject_id:
        lessons = lessons.filter(Lesson.subject_id == subject_id)
    
    if tutor_id:
        lessons = lessons.filter(Lesson.tutor_id == tutor_id)
    
    if family_id:
        # Find all students with the given family_id
        student_ids = [student.StudentID for student in Student.query.filter(Student.family_id == family_id).all()]
        
        # Find all lessons with those student IDs
        lessons = lessons.filter(Lesson.students.any(Student.StudentID.in_(student_ids)))
    
    lessons = lessons.all()
    print(lessons)
    lesson_details = []
    for lesson in lessons:
        tutor_id = lesson.tutor_id
        tutor = Tutor.query.filter_by(tutor_id=tutor_id).first()
        user_id = tutor.user_id
        user = User.query.filter_by(id=user_id).first()
        user_paygrade_id = user.paygrade_id
        paygrade = Paygrade.query.filter_by(id=user_paygrade_id).first()
        if paygrade:
            user_paygrade = paygrade.value
            tutor_payment = int(user_paygrade)
        else:
            tutor_payment = int('0')
        if lesson.final_price is None:
            gross_wage = -tutor_payment
        else:
            gross_wage = lesson.final_price - tutor_payment

        discount_id = lesson.price_adjustment_id
        discount = PriceAdjustment.query.filter_by(id=discount_id).first()
        discount = discount.name if discount else None
        subject_id = lesson.subject_id
        subject = Subject.query.filter_by(subject_id=subject_id).first()
        subject_name = subject.subject_name
        students = lesson.students
        student_names = [f"{student.FirstName} {student.LastName}" for student in students]  # Get the students' names
        lesson_details.append({
            'lesson' : lesson,
            'tutor_payment' : tutor_payment,
            'discount' : discount,
            'gross_wage': gross_wage,
            'tutor_name': tutor.name,
            'subject_name': subject_name,
            'student_names': student_names
        })


    return lesson_details





app = Flask(__name__)
# Database configuration and initialization
app.config.from_object(Config)
db.init_app(app)
with app.app_context():
    db.create_all()

migrate = Migrate(app, db)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)






import phonenumbers

def is_valid_number(phone_number):
    try:
        parsed_number = phonenumbers.parse(phone_number, None)
        return phonenumbers.is_valid_number(parsed_number)
    except phonenumbers.NumberParseException:
        return False


from twilio.rest import Client
from twilio.base.exceptions import TwilioException



def format_number(phone_number):
    try:
        parsed_number = phonenumbers.parse(phone_number, "CH")  # 'CH' is the country code for Switzerland
        formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        return formatted_number
    except phonenumbers.NumberParseException:
        return None  # or handle the error as you prefer


@app.route('/')
def index():
    return render_template('fit4school.html')

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


@app.route('/api/schooltype_for_student/<int:student_id>', methods=['GET'])
@login_required
@admin_required
def get_schooltype_for_student(student_id):
    student = Student.query.get(student_id)
    if student:
        schooltype = SchoolType.query.get(student.schooltype_id)
        if schooltype:
            return jsonify({'schooltype_id': schooltype.schooltype_id, 'schooltype_name': schooltype.schooltype_name})
    return jsonify({}), 404

@app.route('/api/tutors/<int:subject_id>', methods=['GET'])
def get_tutors_for_subject(subject_id):
    # Query to find tutors who can teach the given subject
    tutors = Tutor.query.join(TutorSubject).filter(TutorSubject.subject_id == subject_id).all()
    return jsonify([{'id': tutor.tutor_id, 'name': tutor.name} for tutor in tutors])

from sqlalchemy import func


def create_lesson_type(name, value):
    lesson_type = LessonType(name=name, value=value)
    db.session.add(lesson_type)
    db.session.commit()
    return lesson_type

def is_tutor_available(tutor, date, start_time, end_time):
    # Convert date to weekday ID (0=Monday, 6=Sunday) and adjust to your system (1=Monday)
    weekday_id = date.weekday() + 1

    # Check availability on the given weekday ID
    availabilities = TutorAvailability.query.filter(
        TutorAvailability.tutor_id == tutor.tutor_id,
        TutorAvailability.weekday_id == weekday_id
    ).all()

    if not availabilities:
        return "unavailable"  # Tutor has no availability on this day

    # Convert start_time and end_time to time objects if they are not already
    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time, '%H:%M').time()
    if isinstance(end_time, str):
        end_time = datetime.strptime(end_time, '%H:%M').time()

    for availability in availabilities:
        # Handle cases where availability times are not set or are default (00:00)
        if availability.start_time == time(0, 0) and availability.end_time == time(0, 0):
            # Assuming this means the tutor is available all day
            is_available_all_day = True
        else:
            is_available_all_day = availability.start_time <= start_time and availability.end_time >= end_time

        if is_available_all_day:
            # Check for conflicting lessons
            conflicting_lesson = Lesson.query.filter(
                Lesson.tutor_id == tutor.tutor_id,
                Lesson.date == date,
                Lesson.start_time < end_time,
                Lesson.end_time > start_time
            ).first()

            if conflicting_lesson:
                print("Tutor is available but has a conflicting lesson")
                return "has_conflicting_lesson"  # Tutor is available but has a conflicting lesson
            print("Tutor is available")
            return "available"  # Tutor is available
    print("Tutor is not available due to no matching availabilities")
    return "unavailable"  # Tutor is not available due to no matching availabilities






@app.route('/api/tutors/<int:subject_id>/<date>/<start_time>/<end_time>', methods=['GET'])
def get_tutors_for_subject_and_time(subject_id, date, start_time, end_time):
    start_time = datetime.strptime(start_time, '%H:%M').time()
    end_time = datetime.strptime(end_time, '%H:%M').time()
    date = datetime.strptime(date, '%Y-%m-%d').date()

    tutors = Tutor.query.join(TutorSubject).filter(TutorSubject.subject_id == subject_id).all()

    tutor_data = []
    for tutor in tutors:
        availability_status = is_tutor_available(tutor, date, start_time, end_time)
        if availability_status == "available":
            status = "frei"
        elif availability_status == "unavailable":
            status = "nicht verfügbar"
        else:  # has_conflicting_lesson
            status = "unterrichtet um diese Zeit"

        tutor_data.append({'id': tutor.tutor_id, 'name': tutor.name, 'status': status})

    return jsonify(tutor_data)



@app.route('/api/schooltypes')
def get_schooltypes():
    schooltypes = SchoolType.query.all()
    return jsonify([{'id': st.schooltype_id, 'name': st.schooltype_name} for st in schooltypes])


@app.route('/api/subjects/<int:schooltype_id>')
def get_subjects(schooltype_id):
    subjects = Subject.query.filter_by(schooltype_id=schooltype_id).all()
    return jsonify([{'id': s.subject_id, 'name': s.subject_name} for s in subjects])


#@app.route('/get_tutors/<int:subject_id>', methods=['GET'])
#def get_tutors(subject_id):
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

from flask import jsonify



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
    return db.session.get(User, user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve username and password from the form
        username = request.form['username']
        password = request.form['password']

        # Query the database for the user
        user = User.query.filter_by(username=username).first()

        # Check if the user exists and the password is correct
        if user and user.check_password(password):
            # Log in the user
            login_user(user)
            flash('Logged in successfully.')
            # Redirect to the page the user tried to access
            if user.role.name == 'admin':
                return redirect(url_for('admin_dashboard'))
            if user.role.name == 'tutor':
                tutor = Tutor.query.filter_by(user_id=user.id).first()
                if tutor:
                    return redirect(url_for('tutor_profile'))
                else:
                    # If the tutor profile does not exist, redirect to create tutor profile
                    return redirect(url_for('create_tutor_profile'))

        else:
            # Redirect to the login page if the login failed
            flash('Invalid username or password')
            return redirect(url_for('login'))
    else:
        return render_template('login.html')
    
@app.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_dashboard():

    return render_template('admin_dashboard.html')

@app.route('/detailed_statistics')
@admin_required
def detailed_statistics():
    detailed_statistics = get_detailed_statistics()
    return render_template('detailed_statistics.html', detailed_statistics=detailed_statistics)

@app.route('/create_user', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role_name = request.form['role']
        paygrade_id = request.form.get('paygrade')  # get paygrade from the form

        # Fetch the paygrade from the database if paygrade_id is provided
        paygrade = Paygrade.query.get(paygrade_id) if paygrade_id else None
        paygrade_id = paygrade.id if paygrade else None

        # Call your create_user_with_role function
        message, success = create_user_with_role(username, password, role_name, paygrade_id)
        flash(message, 'success' if success else 'danger')

        if success:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('create_user'))

    paygrades = Paygrade.query.all()  # get all paygrades
    return render_template('create_user.html', paygrades=paygrades)

from flask import jsonify

from flask import render_template, request

@app.route('/tutor/change_password', methods=['GET', 'POST'])
@login_required
@tutor_required
def change_password():
    user_id = current_user.id
    user = User.query.get(user_id)

    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        repeat_password = request.form['repeat_password']

        response_data = {}

        if user.check_password(old_password):
            if new_password == repeat_password:
                password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                user.password_hash = password
                db.session.commit()
                response_data['success'] = True
                response_data['message'] = 'Password updated successfully.'
            else:
                response_data['success'] = False
                response_data['message'] = 'New password and repeat password do not match.'
        else:
            response_data['success'] = False
            response_data['message'] = 'Incorrect old password.'

        return render_template('change_password.html', user=user, response_data=response_data)

    return render_template('change_password.html', user=user)


    

@app.route('/tutor/view_students', methods=['GET'])
@login_required
@tutor_required
def view_students():
    user_id = current_user.id
    tutor_id = Tutor.query.filter_by(user_id=user_id).first().tutor_id

    # Retrieve all students associated with the tutor's lessons
    lessons = Lesson.query.filter_by(tutor_id=tutor_id).all()
    student_ids = {student.StudentID for lesson in lessons for student in lesson.students}
    student_details = {}

    for student_id in student_ids:
        student = Student.query.get(student_id)
        student_lessons = Lesson.query.join(Lesson.students).filter_by(StudentID=student_id).all()

        lessons_info = []
        for lesson in student_lessons:
            subject = Subject.query.filter_by(subject_id=lesson.subject_id).first()
            is_current_tutor = lesson.tutor_id == tutor_id
            lesson_info = {
                'subject_name': subject.subject_name if subject else 'No Subject',
                'date': lesson.date,
                'start_time': lesson.start_time,
                'end_time': lesson.end_time,
                'lesson_id': lesson.lesson_id,
                'is_current_tutor': is_current_tutor
            }
            lessons_info.append(lesson_info)

        student_details[student_id] = {
            'info': student,
            'lessons': lessons_info
        }

    return render_template('view_students.html', student_details=student_details)

@app.route('/tutor/create_report_card/<int:student_id>', methods=['GET', 'POST'])
@login_required
@tutor_required
def create_report_card(student_id):
    student = Student.query.get_or_404(student_id)
    tutor_id = Tutor.query.filter_by(user_id=current_user.id).first().tutor_id

    if request.method == 'POST':
        comments = request.form['comments']

        # Create a new ReportCard instance
        new_report_card = ReportCard(
            student_id=student_id,
            tutor_id=tutor_id,
            comments=comments
        )

        # Add to the database
        db.session.add(new_report_card)
        db.session.commit()

        # Redirect to a confirmation page or back to the student list
        flash('Report card created successfully!', 'success')
        return redirect(url_for('view_students'))

    return render_template('create_report_card.html', student=student)






@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get(user_id)
    if request.method == 'POST':
        return True
    return True




from datetime import datetime
from flask import request, jsonify
from dateutil.parser import parse  # dateutil handles ISO 8601 dates well

@app.route('/api/lessons')
@login_required
@admin_required
def get_lessons():
    start_param = request.args.get('start')
    end_param = request.args.get('end')
    try:
        start_time = parse(start_param) if start_param else None
        end_time = parse(end_param) if end_param else None
    except ValueError:
        return jsonify({'error': 'Invalid date format. Please use ISO 8601 format.'}), 400
    
    if start_time and end_time:
        lessons = Lesson.query.filter(Lesson.date >= start_time, Lesson.date <= end_time).all()
    else:
        lessons = Lesson.query.all()
    
    
    lessons_data = []
    for lesson in lessons:
        tutor = Tutor.query.filter_by(tutor_id=lesson.tutor_id).first()
        subject = Subject.query.filter_by(subject_id=lesson.subject_id).first()

        # Combine date and time for start and end
        start_datetime = datetime.combine(lesson.date, lesson.start_time)
        end_datetime = datetime.combine(lesson.date, lesson.end_time)

        # Determine the color of the event based on whether the lesson has occurred and whether it's in the past or future
        now = datetime.now()
        if lesson.has_occured:
            color = '#90EE90'  # Light green for lessons that have occurred
        elif start_datetime > now:
            color = '#ADD8E6'  # Light blue for lessons in the future that have not occurred
        else:
            color = 'red'  # Red for lessons in the past that have not occurred

        # Initialize an empty list to store student names
        student_names = []

        # Loop over each student in the lesson
        for student_lesson in lesson.students:
            student = Student.query.filter_by(StudentID=student_lesson.StudentID).first()
            # Add the student's name to the list
            student_names.append(f"{student.FirstName} {student.LastName}")

        # Create a string with all student names separated by commas
        student_names_str = ', '.join(student_names)

        # Create the calendar object with the student names in the title
        lessons_data.append({
            'id': lesson.lesson_id,
            'title': f"{subject.subject_name} - {student_names_str} - {tutor.name}",
            'start': start_datetime.isoformat(),
            'end': end_datetime.isoformat(),
            'description': f"Tutor: {tutor.name}, Students: {student_names_str}",
            'color': color
        })
    return jsonify(lessons_data)


@app.route('/tutor_dashboard')
@login_required
def generate_calendar():
    if current_user.role != 'tutor':
        flash("You don't have permission to access this page.")
        return(url_for('index'))

    # Get the current month and year
    now = datetime.now()
    month = now.month
    year = now.year

    # Query the database for all lessons for the current month for the current user
    start_date = datetime(year, month, 1)
    end_date = start_date + timedelta(days=31)
    lessons = Lesson.query.filter_by(tutor_id=current_user.id).filter(Lesson.start_time >= start_date).filter(Lesson.end_time <= end_date).all()

    # Convert the lessons into a format that can be used by the calendar library
    events = []
    for lesson in lessons:
        event = {
            'title': lesson.subject.name,
            'start': lesson.start_time.isoformat(),
            'end': lesson.end_time.isoformat()
        }
        events.append(event)

    return render_template('tutor_dashboard.html', events=events)

from sqlalchemy.orm import joinedload

@app.route('/tutor/lessons')
@login_required
@tutor_required
def tutor_lessons():
    # Fetch the tutor associated with the current user
    tutor = Tutor.query.filter_by(user_id=current_user.id).first()

    # Fetch all lessons associated with this tutor
    lessons = Lesson.query.filter_by(tutor_id=tutor.tutor_id).all()

    # Create a list of lesson dictionaries
    lesson_info = []
    current_date = datetime.now().date()  # Get the current date

    for lesson in lessons:
        subject = Subject.query.filter_by(subject_id=lesson.subject_id).first()
        lesson_date = lesson.date
        has_occurred = lesson.has_occured

        # Check if the lesson is in the past but hasn't occurred yet
        if lesson_date < current_date and not has_occurred:
            lesson_color = 'text-danger'  # Mark lessons in red
        else:
            lesson_color = ''  # No special formatting

        lesson_info.append({
            'date': lesson_date,
            'subject_name': subject.subject_name if subject else 'No Subject',
            'start_time': lesson.start_time,
            'end_time': lesson.end_time,
            'has_occured': has_occurred,
            'id': lesson.lesson_id,
            'lesson_color': lesson_color  # CSS class for formatting
        })

    # Render the template with the lesson info
    return render_template('tutor_lessons.html', lesson_info=lesson_info)



@app.route('/api/lessons/<int:lesson_id>/note', methods=['GET'])
@login_required
def get_lesson_note(lesson_id):
    # Fetch the note associated with the lesson
    note = Note.query.filter_by(lesson_id=lesson_id).first()

    # If the note exists, return it as JSON
    if note:
        return jsonify(note.to_dict())

    # If the note doesn't exist, return an empty JSON object
    return jsonify({})

from flask import request, jsonify

import urllib.parse

@app.route('/api/lesson_status/<int:lesson_id>', methods=['POST'])
def update_lesson_status(lesson_id):
    data = request.get_json()

    # Get the lesson
    lesson = Lesson.query.get(lesson_id)

    if not lesson:
        return jsonify({'message': 'Lesson not found'}), 404


    lesson.has_occured = int(data['has_occurred'])

    # If the lesson has a note, update the content of the first note
    if lesson.notes:
        lesson.notes[0].content = data['note']
    # If the lesson doesn't have a note, create a new note
    else:
    # Get the student_id from the lesson_student association table
        student_id = lesson.students[0].StudentID if lesson.students else None
        note = Note(content=data['note'], lesson_id=lesson_id, tutor_id=lesson.tutor_id, student_id=student_id, subject_id=lesson.subject_id)
        db.session.add(note)

    db.session.commit()

    return jsonify({'message': 'Lesson status and note updated successfully'}), 200

@app.route('/api/lesson_notes/<int:lesson_id>')
def get_lesson_notes(lesson_id):
    notes = Note.query.filter_by(lesson_id=lesson_id).first()
    return jsonify({'notes': notes.content if notes else 'No notes available'})





@app.route('/edit_note/<int:note_id>', methods=['GET', 'POST'])
@login_required
@tutor_required
def edit_note(note_id):
    note = Note.query.get(note_id)
    if request.method == 'POST':
        note.content = request.form['content']
        db.session.commit()
        return redirect(url_for('tutor_lessons'))
    return render_template('edit_note.html', note=note)


@app.route('/admin_lessons', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_lesson():
    lessons = Lesson.query.all()
    lesson_info = [{
        'date': lesson.date,
        'tutor': lesson.tutor.name,
        'subject': lesson.subject.name,

    }for lesson in lessons]

    return render_template('admin_lessons.html', lesson_info=lesson_info)

def edit_lesson():
    pass


@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    # Fetch the user by ID
    user = User.query.get(user_id)
    if user:
        # Delete the user
        user.username = 'geloecht'
        user.password = 'geloecht'
        db.session.commit()
        return jsonify(message='User deleted successfully'), 200
    else:
        return jsonify(message='User not found'), 404

@app.route('/add_schooltype', methods=['GET', 'POST'])
@login_required
@admin_required
def add_schooltype():
    if request.method == 'POST':
        schooltype_name = request.form.get('schooltype_name')
        new_schooltype = SchoolType(schooltype_name=schooltype_name)
        db.session.add(new_schooltype)
        db.session.commit()
        # Redirect or notify of success
        return redirect(url_for('modify_subjects'))
    return render_template('create_schooltype.html')

@app.route('/add_subject', methods=['GET', 'POST'])
@login_required
@admin_required
def add_subject():
    schooltypes = SchoolType.query.all()

    if request.method == 'POST':
        subject_name = request.form.get('subject_name')
        schooltype_id = request.form.get('schooltype_id')

        if schooltype_id:
            schooltype_id = int(schooltype_id)  # Convert to integer
            new_subject = Subject(schooltype_id=schooltype_id, subject_name=subject_name)
            db.session.add(new_subject)
            db.session.commit()
            return redirect(url_for('modify_subjects'))
            # Redirect or notify of success
        else:
            # Handle the case where school type is not selected
            pass

    return render_template('create_subject.html', schooltypes=schooltypes)


@app.route('/modify_subjects')
@login_required
@admin_required
def modify_subjects():
    subjects = Subject.query.join(SchoolType).order_by(SchoolType.schooltype_name, Subject.subject_name).all()
    return render_template('modify_subjects.html', subjects=subjects)

@app.route('/delete_subject/<int:subject_id>', methods=['POST'])
@login_required
@admin_required
def delete_subjectt(subject_id):
    subject = Subject.query.get(subject_id)
    if subject:
        db.session.delete(subject)
        db.session.commit()
        return jsonify(message='Erfolgreich gelöscht'), 200
    else:
        return jsonify(message='Subject not found'), 404

@app.route('/modify_family')
@login_required
@admin_required
def modify_family():
    families = Family.query.order_by(Family.name).all()
    for family in families:
        family.students = Student.query.filter_by(family_id=family.id).all()
    return render_template('modify_family.html', families=families)


@app.route('/register_family', methods=['GET', 'POST'])
@login_required
@admin_required
def register_family():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        phone_num = request.form.get('phone_num')

        new_family = Family(name=name, address=address, phone_num=phone_num)
        db.session.add(new_family)
        db.session.commit()
    return render_template('create_family.html')

@app.route('/edit_family/<int:family_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_family(family_id):
    family = Family.query.get(family_id)
    if request.method == 'POST':
        family.name = request.form.get('name')
        family.address = request.form.get('address')
        family.phone_num = request.form.get('phone_num')
        entrance_day_str = request.form.get('entrance_day')
        if entrance_day_str:
            family.entrance_day = datetime.strptime(entrance_day_str, '%Y-%m-%d').date()
        else:
            family.entrance_day = None
        db.session.commit()
        return redirect(url_for('modify_family'))
    return render_template('edit_family.html', family=family)

@app.route('/add_student_to_family/<int:family_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def add_student_to_family(family_id):
    schooltypes = SchoolType.query.all()
    family = Family.query.get(family_id)
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        schooltype_id = request.form.get('schooltype_id')
        date_of_birth_str = request.form.get('date_of_birth')
        date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d') if date_of_birth_str else None
        if not date_of_birth:
            flash('Date of birth is required', 'error')
            return redirect(request.url)
        phone_num = request.form.get('phone_num')
        new_student = Student(FirstName=first_name, LastName=last_name, schooltype_id=schooltype_id, DateOfBirth=date_of_birth, family_id=family_id, phone_num=phone_num)
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('modify_family'))

    return render_template('add_student_to_F.html', family=family, schooltypes=schooltypes)

@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_student(student_id):
    student = Student.query.get(student_id)
    schooltypes = SchoolType.query.all()
    if request.method == 'POST':
        student = Student.query.get(student_id)
        student.FirstName = request.form.get('first_name')
        student.LastName = request.form.get('last_name')
        student.DateOfBirth = request.form.get('date_of_birth')
        student.schooltype_id = request.form.get('schooltype_id')
        student.phone_num = request.form.get('student_num')
        db.session.commit()
        return redirect(url_for('modify_family'))
    return render_template('edit_student.html', student=student, schooltypes=schooltypes)


@app.route('/admin/report_cards')
@login_required
@admin_required
def admin_report_cards():
    report_cards = ReportCard.query.all()
    return render_template('admin_report_cards.html', report_cards=report_cards)

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from io import BytesIO
from reportlab.lib.styles import ParagraphStyle

@app.route('/admin/download_report_card/<int:report_card_id>')
def download_report_card(report_card_id):
    report_card = ReportCard.query.get_or_404(report_card_id)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    Story = []

    # Create custom styles
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontSize=12, leading=15, spaceAfter=6, bold=True)

    # Use the custom style for headers
    Story.append(Paragraph(f"Datum: {report_card.date_created.strftime('%Y-%m-%d')}", header_style))
    Story.append(Paragraph(f"Tutor: {report_card.tutor.name}", header_style))
    Story.append(Paragraph(f"Schüler*in: {report_card.student.FirstName} {report_card.student.LastName}", header_style))
    Story.append(Spacer(1, 12))

    # Handling multiline comments
    comment_style = styles['Normal']
    comment_style.wordWrap = 'CJK'  # This helps with word wrapping
    Story.append(Paragraph(f"Inhalt: {report_card.comments}", comment_style))

    doc.build(Story)

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'Berciht_{report_card_id}.pdf', mimetype='application/pdf')








from datetime import datetime, timedelta


def filter_lessons_in_range(from_date, end_date, school_type_id=None, subject_id=None, tutor_id=None):
    lessons = Lesson.query.filter(Lesson.date.between(from_date, end_date))
    if school_type_id:
        subject_ids = [subject.subject_id for subject in Subject.query.filter_by(schooltype_id=school_type_id)]
        lessons = lessons.filter(Lesson.subject_id.in_(subject_ids))
    if subject_id:
        lessons = lessons.filter(Lesson.subject_id == subject_id)
    if tutor_id:
        lessons = lessons.filter(Lesson.tutor_id == tutor_id)
    return lessons.all()

@app.route('/modify_lessons', methods=['GET', 'POST'])
@login_required
@admin_required
def modify_lessons():
    today = datetime.now()
    from_date = datetime(today.year, today.month, today.day)
    to_date = datetime(today.year, today.month, today.day) + timedelta(days=7)
    schooltype_id = None
    subject_id = None
    tutor_id = None
    lessons = filter_lessons_in_range(from_date, to_date, schooltype_id, subject_id, tutor_id)
    from_date = from_date.strftime('%Y-%m-%d')
    to_date = to_date.strftime('%Y-%m-%d')

    if request.method == 'POST':
        from_date = datetime(today.year, today.month, 1)
        to_date = datetime(today.year, today.month, 1) + relativedelta(months=1) - timedelta(days=1)
        if request.form.get('from_date') and request.form.get('to_date') is not None: 
            from_date = datetime.strptime(request.form.get('from_date'), '%Y-%m-%d')
            to_date = datetime.strptime(request.form.get('to_date'), '%Y-%m-%d')
        student_id = request.form.get('student_id')
        tutor_id = request.form.get('tutor_id')

        # Convert the IDs to integers if they are not None or an empty string

        student_id = None
        if tutor_id == 'Alle':
            tutor_id = None
        else:
            if tutor_id is not None:
                tutor_id = int(tutor_id)



        
        lessons = filter_lessons_in_range(from_date, to_date, schooltype_id, subject_id, tutor_id)

    formatted_lessons = []
    for lesson in lessons:
        tutor = Tutor.query.get(lesson.tutor_id)
        students = lesson.students.all()
        subject = Subject.query.get(lesson.subject_id)
        student_names = ', '.join([f"{student.FirstName} {student.LastName}" for student in students])
        formatted_lessons.append({
            'lesson_id': lesson.lesson_id,
            'date': lesson.date.strftime('%Y-%m-%d'),
            'start_time': lesson.start_time.strftime('%H:%M'),
            'end_time': lesson.end_time.strftime('%H:%M'),
            'tutor_name': tutor.name,
            'student_name': student_names,
            'subject_name': subject.subject_name,
            'has_occurred': lesson.has_occured,
            'notes': lesson.notes
        })

    all_tutors = Tutor.query.all()
    all_students = Student.query.all()
    formatted_lessons.sort(key=lambda x: (x['date'], x['start_time']))
    
    return render_template('modify_lessons.html', lessons=formatted_lessons, from_date=from_date, to_date=to_date, tutors=all_tutors, students=all_students, tutor_id=tutor_id)


@app.route('/delete_lesson/<int:lesson_id>', methods=['POST'])
def delete_lesson(lesson_id):
    lesson = Lesson.query.get(lesson_id)
    if lesson:
        for student in lesson.students:
            lesson.students.remove(student)
        Note.query.filter_by(lesson_id=lesson_id).delete()
        Contacted.query.filter_by(lesson_id=lesson_id).delete()
        db.session.delete(lesson)
        db.session.commit()

        redirect_url = url_for('admin_dashboard') if current_user.role.name == 'admin' else url_for('tutor_lessons')
        return jsonify({'message': 'Lesson deleted successfully', 'redirect_url': redirect_url}), 200
    else:
        return jsonify({'message': 'Lesson not found'}), 404



@app.route('/tutor/delete_subject/<int:subject_id>', methods=['POST'])
@tutor_required
@login_required
def delete_subject(subject_id):
    user_id = current_user.id
    tutor = Tutor.query.filter_by(user_id=user_id).first()
    tutor_subject = TutorSubject.query.filter_by(tutor_id=tutor.tutor_id, subject_id=subject_id).first()
    if tutor_subject:
        db.session.delete(tutor_subject)
        db.session.commit()
    return redirect(url_for('edit_tutor'))


@app.route('/modify_users')
@login_required
@admin_required
def modify_users():
    users = User.query.all()
    user_data = []

    for user in users:
        is_tutor = Tutor.query.filter_by(user_id=user.id).first() is not None
        user_data.append({
            'user_id': user.id,
            'username': user.username,
            'role': user.role.name,
            'is_tutor': is_tutor
        })

    return render_template('modify_users.html', users=user_data)

import math
def round_to_nearest_five_cents(amount):
    # Rounds the amount to the nearest .05
    return round(amount * 20) / 20.0


@app.route('/add_lesson', defaults={'lesson_id': None}, methods=['GET', 'POST'])
@app.route('/add_lesson/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def add_lesson(lesson_id):
    lesson = Lesson.query.get(lesson_id) if lesson_id else None
    prepopulated_data = {}
    if lesson:
        subject_id = lesson.subject_id
        subject = Subject.query.get(subject_id)
        schooltype_id = subject.schooltype_id
        prepopulated_data = {
            'date': lesson.date,
            'start_time': lesson.start_time,
            'end_time': lesson.end_time,	
            'tutor_id': lesson.tutor_id,
            'subject_id': lesson.subject_id,
            'schooltype_id': schooltype_id,
            'student_ids': [student.StudentID for student in lesson.students],
            'price': lesson.price,
            'price_adjustment_id': lesson.price_adjustment_id
        }

    if request.method == 'POST':
        date = request.form.get('date')
        date = datetime.strptime(date, '%Y-%m-%d').date()
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        #calculate duration with endtime and starttime
        duration = (datetime.strptime(end_time, '%H:%M') - datetime.strptime(start_time, '%H:%M')).seconds / 3600
        tutor_id = request.form.get('tutor_id')
        student_id = request.form.get('student_id')
        subject_id = request.form.get('subject_id')
        price = request.form.get('price')
        
        price_adjustment_id = request.form.get('price_adjustment_id')
        price_adjustment = PriceAdjustment.query.get(price_adjustment_id)
        if price_adjustment is None:
            adjustment_value = 0
        else:
            adjustment_value = price_adjustment.value
        ferienkurs = request.form.get('ferienkurs') is not None
        ferienkurs_2 = request.form.get('ferienkurs_2') is not None

        student_ids = request.form.getlist('student_ids')
        if ferienkurs == True:
            for i in range(0,4):
                new_lesson = Lesson(
                    date=date + timedelta(days=i),
                    start_time=start_time,
                    end_time=end_time,
                    tutor_id=tutor_id,
                    subject_id=subject_id,
                    price=111,
                    price_adjustment_id=3,
                    final_price = 111,
                    lesson_type_id = 3
                )

                for student_id in student_ids:
                    student = Student.query.get(student_id)
                    student.enrolled_lessons.append(new_lesson)

                db.session.add(new_lesson)
            db.session.commit()
            return redirect(url_for('modify_lessons'))
        
        if ferienkurs_2 == True:
            for i in range(0,5):
                new_lesson = Lesson(
                    date=date + timedelta(days=i),
                    start_time=start_time,
                    end_time=end_time,
                    tutor_id=tutor_id,
                    subject_id=subject_id,
                    price=69,
                    price_adjustment_id=3,
                    final_price = 110,
                    lesson_type_id = 3
                )
                for student_id in student_ids:
                    student = Student.query.get(student_id)
                    student.enrolled_lessons.append(new_lesson)

                db.session.add(new_lesson)
            db.session.commit()
            return redirect(url_for('modify_lessons'))
                    
        if len(student_ids) > 1:
            new_lesson = Lesson(
                date=date,
                start_time=start_time,
                end_time=end_time,
                tutor_id=tutor_id,
                subject_id=subject_id,
                price=price,
                final_price = round_to_nearest_five_cents(float(price) * duration * (1 - adjustment_value)),
                lesson_type_id = 2 
            )
            for student_id in student_ids:
                student = Student.query.get(student_id)
                student.enrolled_lessons.append(new_lesson)
            db.session.add(new_lesson)
            db.session.commit()
            return redirect(url_for('modify_lessons'))


        else:
            new_lesson = Lesson(
                date=date,
                start_time=start_time,
                end_time=end_time,
                tutor_id=tutor_id,
                subject_id=subject_id,
                price=price,
                price_adjustment_id=price_adjustment_id,
                final_price = round_to_nearest_five_cents(float(price) * duration * (1 - adjustment_value)),
                lesson_type_id = 1
            )
            for student_id in student_ids:
                student = Student.query.get(student_id)
                student.enrolled_lessons.append(new_lesson) # Add the lesson to the student's enrolled lessons
            db.session.add(new_lesson)
            db.session.commit()
            return redirect(url_for('modify_lessons'))

    
    students = Student.query.order_by(Student.LastName).all()
    price_adjustments = PriceAdjustment.query.all()
    schooltypes = SchoolType.query.all()
    return render_template('add_lesson.html', students=students, price_adjustments=price_adjustments, schooltypes=schooltypes, prepopulated_data=prepopulated_data)

@app.route('/tutor/add_lesson/lesson/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
@tutor_required
def add_lesson_based_on_existing(lesson_id):
    students = []
    tutor_id = Tutor.query.filter_by(user_id=current_user.id).first().tutor_id
    if lesson_id:
        lesson = Lesson.query.get_or_404(lesson_id)
        schooltype = Subject.query.get(lesson.subject_id).schooltype
        for student in lesson.students:
            students.append(student)
        prepopulated_data = {
            'date': lesson.date.strftime('%Y-%m-%d'),
            'start_time': lesson.start_time.strftime('%H:%M'),
            'end_time': lesson.end_time.strftime('%H:%M'),
            'schooltype_id': schooltype.schooltype_id,
            'subject_id': lesson.subject_id,
        }

    if request.method == 'POST':
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        subject_id = request.form.get('subject_id')

        # Fetch the last lesson's pricing details
        last_lesson = lesson
        if last_lesson:
            price = last_lesson.price
            price_adjustment_id = last_lesson.price_adjustment_id
            final_price = last_lesson.final_price
        else:
            # Default pricing if no last lesson exists
            price = 0
            price_adjustment_id = None
            final_price = 0

        new_lesson = Lesson(
            date=date,
            start_time=start_time,
            end_time=end_time,
            tutor_id=tutor_id,
            subject_id=subject_id,
            price=price,
            price_adjustment_id=price_adjustment_id,
            final_price=final_price
        )

        # Associate the student with the lesson
        if students:
            for student in students:
                new_lesson.students.append(student)

        db.session.add(new_lesson)
        db.session.commit()

        return redirect(url_for('view_students'))  # Redirect to an appropriate page
    subjects = Subject.query.all()  # Assuming you have a Subject model
    schooltypes = SchoolType.query.all()
    return render_template('tutor_add_lesson_for_student.html', students=students, subjects=subjects, schooltypes=schooltypes, prepopulated_data=prepopulated_data)
    



@app.route('/tutor/add_lesson/student/<int:student_id>', methods=['GET', 'POST'])
@login_required
@tutor_required
def add_lesson_for_student(student_id):
    students = []
    prepopulated_data = {}
    student_prime = Student.query.get_or_404(student_id)
    tutor_id = Tutor.query.filter_by(user_id=current_user.id).first().tutor_id
    if request.method == 'POST':
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        subject_id = request.form.get('subject_id')

        # Fetch the last lesson's pricing details
        last_lesson = Lesson.query.filter(Lesson.students.any(StudentID=student_id)).order_by(Lesson.date.desc()).first()
        if last_lesson:
            price = last_lesson.price
            price_adjustment_id = last_lesson.price_adjustment_id
            final_price = last_lesson.final_price
        else:
            # Default pricing if no last lesson exists
            price = 0
            price_adjustment_id = None
            final_price = 0

        new_lesson = Lesson(
            date=date,
            start_time=start_time,
            end_time=end_time,
            tutor_id=tutor_id,
            subject_id=subject_id,
            price=price,
            price_adjustment_id=price_adjustment_id,
            final_price=final_price
        )
        new_lesson.students.append(student_prime)

        db.session.add(new_lesson)
        db.session.commit()

        return redirect(url_for('view_students'))  # Redirect to an appropriate page
    students.append(student_prime)
    subjects = Subject.query.all()  # Assuming you have a Subject model
    schooltypes = SchoolType.query.all()
    return render_template('tutor_add_lesson_for_student.html', students=students, subjects=subjects, schooltypes=schooltypes, prepopulated_data=prepopulated_data)




from datetime import datetime

@app.route('/api/find_tutors/<int:subject_id>/<date_str>/<start_time_str>/<end_time_str>', methods=['GET'])
def find_tutors(subject_id, date_str, start_time_str, end_time_str):
    # Convert string to date and time objects
    lesson_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    start_time = datetime.strptime(start_time_str, '%H:%M').time()
    end_time = datetime.strptime(end_time_str, '%H:%M').time()

    # Step 1: Get tutors who can teach the subject
    tutors_for_subject = Tutor.query.join(TutorSubject).filter(TutorSubject.subject_id == subject_id).all()

    # Step 2: Filter based on availability
    available_tutors = []
    for tutor in tutors_for_subject:
        if is_tutor_available(tutor.tutor_id, lesson_date, start_time, end_time):
            available_tutors.append(tutor)

    # Prepare data for JSON response
    tutor_data = [{'id': tutor.tutor_id, 'name': tutor.name} for tutor in available_tutors]

    return jsonify(tutor_data)

@app.route('/api/tutor_lessons', methods=['GET'])
@login_required
def api_tutor_lessons():
    # Get the logged in tutor's ID
    user_id = current_user.id
    tutor = Tutor.query.filter_by(user_id=user_id).first()

    # Get the lessons for this tutor
    lessons = Lesson.query.filter_by(tutor_id=tutor.tutor_id).all()

    # Convert the lessons to the format expected by FullCalendar
    lesson_data = []
    for lesson in lessons:
        # Query the subject name separately
        subject = Subject.query.filter_by(subject_id=lesson.subject_id).first()

        # Combine date and time for start and end
        start_datetime = datetime.combine(lesson.date, lesson.start_time)
        end_datetime = datetime.combine(lesson.date, lesson.end_time)

        # Determine the color of the event based on whether the lesson has occurred
        now = datetime.now()
        if lesson.has_occured:
            color = '#90EE90'  # Light green for lessons that have occurred
        elif start_datetime > now:
            color = '#ADD8E6'  # Light blue for lessons in the future that have not occurred
        else:
            color = 'red'  # Red for lessons in the past that have not occurred

        for student_lesson in lesson.students:
            student = Student.query.filter_by(StudentID=student_lesson.StudentID).first()

            lesson_data.append({
                'id': lesson.lesson_id,
                'title': f"{subject.subject_name} - {student.LastName} - {tutor.name}",
                'start': start_datetime.isoformat(),
                'end': end_datetime.isoformat(),
                'description': f"Tutor: {tutor.name}, Student: {student.FirstName} {student.LastName}",
                'color': color
            })

    # Return the data as JSON
    return jsonify(lesson_data)


@app.template_filter('formatdate')
def format_date(value, format='%d-%m-%Y'):
    return datetime.strptime(value, '%Y-%m-%d').strftime(format)

from collections import defaultdict
from models import check_promotion_usage

@app.route('/api/check_promotion_usage/<int:student_id>', methods=['GET'])
def api_check_promotion_usage(student_id):
    used = check_promotion_usage(student_id)
    return jsonify({'used': used})





@app.route('/tutor/edit_tutor', methods=['GET', 'POST'])
@login_required
@tutor_required
def edit_tutor():
    tutor = Tutor.query.filter_by(user_id=current_user.id).first()
    subjects = Subject.query.join(TutorSubject).filter(TutorSubject.tutor_id == tutor.tutor_id).all()

    if request.method == 'POST':
        # Delete all existing availability times for the tutor
        TutorAvailability.query.filter_by(tutor_id=tutor.tutor_id).delete()
        
        for day_id in range(1, 7):
            # Retrieve time inputs for the single slot
            start_time = request.form.get(f'start_time_{day_id}')
            end_time = request.form.get(f'end_time_{day_id}')
            # Check if both start and end times are provided
            if start_time and end_time:
                availability = TutorAvailability(tutor_id=tutor.tutor_id, weekday_id=day_id, start_time=start_time, end_time=end_time)
                db.session.add(availability)

        phone_num = request.form.get('phone_num')
        if phone_num:
            tutor.phone_num = phone_num
        db.session.commit()
        return redirect(url_for('edit_tutor'))

    times_raw = TutorAvailability.query.filter_by(tutor_id=tutor.tutor_id).all()
    
    times_by_day = defaultdict(list)
    for time in times_raw:
        times_by_day[time.weekday_id].append(time)

    # Prepare structured times for the template
    structured_times = {}
    for day_id in range(1, 7):  # For 6 weekdays
        day_times = times_by_day.get(day_id, [])
        time = day_times[0] if len(day_times) > 0 and day_times[0].start_time != '00:00:00' else None
        structured_times[day_id] = time

    # Debug print
    for day_id, time in structured_times.items():
        print(f"Day {day_id}: {time}")

    return render_template('edit_tutor.html', tutor=tutor, subjects=subjects, times=structured_times)



def query_lessons(date, tutor_id):
    lessons = Lesson.query.filter_by(date=date, tutor_id=tutor_id).all()
    return lessons

@app.route('/tutor_profile/', methods=['GET', 'POST'])
@login_required
@tutor_required
def tutor_profile():
    tutor = Tutor.query.filter_by(user_id=current_user.id).first()
    if Tutor.query.filter_by(user_id=current_user.id).first() is None:
        #create tutor profile for this user (redirect to create tutor profile page)
        return redirect(url_for('create_tutor_profile'))
    if tutor.user_id != current_user.id:
        flash("You don't have permission to access this page.")
        return redirect(url_for('index'))
    else:
        return render_template('tutor_profile.html', tutor=tutor)




@app.route('/tutor/subject/<int:tutor_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def tutor_edit_subjects(tutor_id):
    tutor = Tutor.query.filter_by(user_id=tutor_id).first()
    user = User.query.filter_by(id=tutor.user_id).first()


    if request.method == 'POST':
        pass #TODO 
    
    


    return render_template('edit_tutor_subjects.html')

@app.route('/tutor/<int:tutor_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def tutor_profil_id(tutor_id):
    tutor = Tutor.query.filter_by(user_id=tutor_id).first()
    user = User.query.filter_by(id=tutor.user_id).first()

    if request.method == 'POST':
        # Delete existing availability times
        TutorAvailability.query.filter_by(tutor_id=tutor.tutor_id).delete()

        # Create new availability times based on form data
        for i in range(1, 8):
            start_time = request.form.get(f'start_time_{i}')
            end_time = request.form.get(f'end_time_{i}')
            if start_time and end_time:
                availability = TutorAvailability(tutor_id=tutor.tutor_id, weekday_id=i, start_time=start_time, end_time=end_time)
                db.session.add(availability)

        paygrade_id = request.form.get('paygrade')
        if paygrade_id:
            user.paygrade_id = paygrade_id

        phone_num = request.form.get('phone_num')
        if phone_num:
            tutor.phone_num = phone_num
        db.session.commit()

    availabilities = TutorAvailability.query.filter_by(tutor_id=tutor.tutor_id).all()
    sorted_availabilities = {i: '00:00 - 00:00' for i in range(1, 8)}  # Initialize with default values

    # Populate the sorted_availabilities dictionary with actual availability
    for availability in availabilities:
        time_slot = f"{availability.start_time} - {availability.end_time}"
        sorted_availabilities[availability.weekday_id] = time_slot

    subjects = TutorSubject.query.filter_by(tutor_id=tutor.tutor_id).all()
    subject_names =  Subject.query.all()
    subject_names_dict = {subject.subject_id: subject.subject_name for subject in subject_names}

    for subject in subjects:
        subject_obj = Subject.query.filter_by(subject_id=subject.subject_id).first()
        schooltype = SchoolType.query.filter_by(schooltype_id=subject_obj.schooltype_id).first()
        subject.schooltype_name = schooltype.schooltype_name

    lessons = Lesson.query.filter_by(tutor_id=tutor.tutor_id).all()
    weekdays = Weekday.query.order_by(Weekday.weekday_id).all()  # Get all

    paygrades = Paygrade.query.all()
    paygrade = Paygrade.query.filter_by(id=user.paygrade_id).first()
    return render_template('admin_tutor_profile.html', tutor=tutor, sorted_availabilities=sorted_availabilities, subjects=subjects, lessons=lessons, weekdays=weekdays, subject_names_dict=subject_names_dict, paygrades=paygrades, paygrade=paygrade, user=user)

@app.route('/tutor/<int:tutor_id>/add_subject', methods=['GET', 'POST'])
@login_required
@admin_required
def tutor_add_subjectt(tutor_id):
    tutor = Tutor.query.filter_by(tutor_id=tutor_id).first()
    user = User.query.filter_by(id=tutor.user_id).first()
    #we will have 2 dropdowns, subject dependent on schooltype, so we need to get all schooltypes and subjects
    schooltypes = SchoolType.query.all()
    subjects = Subject.query.all()
    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        tutor_subject = TutorSubject(tutor_id=tutor.tutor_id, subject_id=subject_id)
        db.session.add(tutor_subject)
        db.session.commit()
        return(redirect(url_for('tutor_profil_id', tutor_id=user.id)))


        
    return(render_template('tutor_add_subjectt.html', tutor=tutor, schooltypes=schooltypes, subjects=subjects))

from datetime import datetime
from flask import request, redirect, url_for, flash, render_template
from datetime import datetime, timedelta

@app.route('/create_tutor_profile', methods=['GET', 'POST'])
@login_required
def create_tutor_profile():
    schooltypes = SchoolType.query.all()
    weekdays = Weekday.query.order_by(Weekday.weekday_id).all()  # Get all weekdays from the database in order
    if request.method == 'POST':
        # Get the current user's tutor profile or create a new one
        tutor_name = request.form.get('name')
        tutor = Tutor.query.filter_by(user_id=current_user.id).first()
        if not tutor:
            tutor = Tutor(name = tutor_name, user_id = current_user.id)
            db.session.add(tutor)
            db.session.commit()
        
        selected_subject_ids = request.form.get('selected_subject_ids', '')
        if selected_subject_ids:
            subject_ids = selected_subject_ids.split(',')
            for subject_id in subject_ids:
                if subject_id:
                    tutor_subject = TutorSubject(tutor_id=tutor.tutor_id, subject_id=int(subject_id))
                    db.session.add(tutor_subject)
        db.session.commit()

        flash('Tutor profile created successfully!', 'success')
        return redirect(url_for('tutor_profile'))

    return render_template('create_tutor_profile.html', schooltypes=schooltypes, weekdays=weekdays)


@app.route('/tutor/create_report', methods=['GET', 'POST'])
@login_required
@tutor_required

def create_report(student_id):
    student = Student.query.filter_by(studentID = student_id).first()
    user_id = current_user.id
    tutor = Tutor.query.filter_by(user_id=user_id).first()
    if request.method == 'POST':
        content = request.form.get('content')
        date = request.form.get('date')
        tutor_id = tutor.tutor_id
        student_id = student.studentID


@app.route('/tutor/add_subject', methods=['GET', 'POST'])
@login_required
@tutor_required
def tutor_add_subject():
    tutor = Tutor.query.filter_by(user_id=current_user.id).first()
    schooltypes = SchoolType.query.all()
    if request.method == 'POST':
        selected_subject_ids = request.form.get('selected_subject_ids', '')
        if selected_subject_ids:
            subject_ids = selected_subject_ids.split(',')
            for subject_id in subject_ids:
                if subject_id:
                    tutor_subject = TutorSubject(tutor_id=tutor.tutor_id, subject_id=int(subject_id))
                    db.session.add(tutor_subject)
        db.session.commit()
        flash('Subject added successfully!', 'info')
        return redirect(url_for('edit_tutor'))
    return render_template('tutor_add_subject.html', tutor=tutor, schooltypes=schooltypes)





from dateutil.relativedelta import relativedelta



from datetime import date

@app.route('/admin/financess', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_financess():
    display_lessons = []
    today = datetime.now()
    from_date = datetime(today.year, today.month, 1)
    end_date = datetime(today.year, today.month, 1) + relativedelta(months=1) - timedelta(days=1)
    school_type = None
    subject_id = None
    family_id = None
    filter_tutor_id = None
    lessons = get_lessons_in_range(from_date, end_date, subject_id, family_id, filter_tutor_id)
    tutors = {lesson['lesson'].tutor_id: Tutor.query.get(lesson['lesson'].tutor_id) for lesson in lessons}
    for lesson in lessons:
        num_students = len(lesson['lesson'].students.all())
        for i, student in enumerate(lesson['lesson'].students.all()):
            display_lesson = {}
            #convert date to dd-mm-yyyy
            lesson_date = lesson['lesson'].date.strftime('%d-%m-%Y')
            display_lesson['date'] = lesson_date
            display_lesson['subject_name'] = Subject.query.get(lesson['lesson'].subject_id).subject_name
            display_lesson['tutor_name'] = Tutor.query.get(lesson['lesson'].tutor_id).name
            display_lesson['student_name'] = f"{student.FirstName} {student.LastName}"
            display_lesson['price'] = lesson['lesson'].price / num_students if 'price' in lesson['lesson'].__dict__ else 0
            price_adjustment_id = lesson['lesson'].price_adjustment_id
            price_adjustment = PriceAdjustment.query.get(price_adjustment_id)
            discount = price_adjustment.value if price_adjustment else 0
            display_lesson['discount'] = f"{discount * 100}%"
            display_lesson['final_price'] = lesson['lesson'].final_price / num_students if 'final_price' in lesson['lesson'].__dict__ else 0
            if i == 0:
                if lesson['lesson'].has_occured == True:
                    tutor_id = lesson['lesson'].tutor_id
                    tutor = tutors[tutor_id]
                    user_id = tutor.user_id
                    user = User.query.filter_by(id=user_id).first()
                    paygrade = Paygrade.query.filter_by(id=user.paygrade_id).first()
                    start_datetime = datetime.combine(date.today(), lesson['lesson'].start_time)
                    end_datetime = datetime.combine(date.today(), lesson['lesson'].end_time)
                    duration_seconds = (end_datetime - start_datetime).total_seconds()
                    duration_hours = duration_seconds / 3600
                    display_lesson['tutor_payment'] = paygrade.value * duration_hours
                else:
                    display_lesson['tutor_payment'] = 0  # Set tutor_payment to 0 if lesson didn't occur
            else:
                display_lesson['tutor_payment'] = 0
            display_lesson['gross_wage'] = display_lesson['final_price'] - display_lesson['tutor_payment']
            display_lessons.append(display_lesson)
    if request.method == 'POST':
        display_lessons = []
        from_date_str = request.form.get('from_date')
        end_date_str = request.form.get('end_date')
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        school_type = request.form.get('school_type')
        subject_id = request.form.get('subject_id')
        family_id = request.form.get('family_id')
        tutor_id = request.form.get('tutor_id')

        # Convert the IDs to integers if they are not None or an empty string
        subject_id = int(subject_id) if subject_id else None
        school_type = int(school_type) if school_type else None
        family_id = int(family_id) if family_id else None
        filter_tutor_id = int(tutor_id) if tutor_id else None
        
        lessons = get_lessons_in_range(from_date, end_date, subject_id, family_id, filter_tutor_id)
        for lesson in lessons:
            num_students = len(lesson['lesson'].students.all())
            for i, student in enumerate(lesson['lesson'].students.all()):
                display_lesson = {}
                display_lesson['date'] = lesson['lesson'].date
                display_lesson['subject_name'] = Subject.query.get(lesson['lesson'].subject_id).subject_name
                display_lesson['tutor_name'] = Tutor.query.get(lesson['lesson'].tutor_id).name
                display_lesson['student_name'] = f"{student.FirstName} {student.LastName}"
                display_lesson['price'] = lesson['lesson'].price / num_students if 'price' in lesson['lesson'].__dict__ else 0
                price_adjustment_id = lesson['lesson'].price_adjustment_id
                price_adjustment = PriceAdjustment.query.get(price_adjustment_id)
                discount = price_adjustment.value if price_adjustment else 0
                display_lesson['discount'] = f"{discount * 100}%"
                display_lesson['final_price'] = lesson['lesson'].final_price / num_students if 'final_price' in lesson['lesson'].__dict__ else 0
                if i == 0:
                    if lesson['lesson'].has_occured == True:
                        tutor_id = lesson['lesson'].tutor_id
                        tutor = tutors[tutor_id]
                        user_id = tutor.user_id
                        user = User.query.filter_by(id=user_id).first()
                        paygrade = Paygrade.query.filter_by(id=user.paygrade_id).first()
                        start_datetime = datetime.combine(date.today(), lesson['lesson'].start_time)
                        end_datetime = datetime.combine(date.today(), lesson['lesson'].end_time)
                        duration_seconds = (end_datetime - start_datetime).total_seconds()
                        duration_hours = duration_seconds / 3600
                        display_lesson['tutor_payment'] = paygrade.value * duration_hours
                    else:
                        display_lesson['tutor_payment'] = 0  # Set tutor_payment to 0 if lesson didn't occur
                else:
                    display_lesson['tutor_payment'] = 0
                display_lesson['gross_wage'] = display_lesson['final_price'] - display_lesson['tutor_payment']
                display_lessons.append(display_lesson)
    users = {tutor.user_id: User.query.get(tutor.user_id) for tutor in tutors.values()}
    paygrades = Paygrade.query.all()
    schooltypes = SchoolType.query.all()
    families = Family.query.all()
    all_tutors = Tutor.query.all()    
    finances = Finance.query.filter(Finance.date.between(from_date, end_date)).all()
    lesson_schooltypes = {lesson['lesson'].lesson_id: SchoolType.query.get(Subject.query.get(lesson['lesson'].subject_id).schooltype_id) for lesson in lessons}
    return render_template('admin_finances.html', lessons=display_lessons, tutors=tutors, users=users, paygrades=paygrades, schooltypes=schooltypes, families=families, all_tutors=all_tutors, default_from_date=from_date.strftime('%Y-%m-%d'), default_end_date=end_date.strftime('%Y-%m-%d'), submitted_school_type_id=school_type, submitted_family_id=family_id, submitted_tutor_id=filter_tutor_id, lesson_schooltypes=lesson_schooltypes, finances=finances)


@app.route('/admin/finances/', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_finances():
    display_lessons = []
    total_fp = 0
    total_profit = 0
    today = datetime.now()
    from_date = datetime(today.year, today.month, 1)
    end_date = datetime(today.year, today.month, 1) + relativedelta(months=1) - timedelta(days=1)
    lessons = get_lessons_in_range(from_date, end_date, None, None, None)
    if request.method == 'POST':
        from_date_str = request.form.get('from_date')
        end_date_str = request.form.get('end_date')
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        lessons = get_lessons_in_range(from_date, end_date, None, None, None)
    for lesson in lessons:
        display_lesson = {}
        has_occured = lesson['lesson'].has_occured
        #convert date to dd/mm/yyyy
        lesson_date = lesson['lesson'].date.strftime('%d/%m/%Y')
        display_lesson['date'] = lesson_date
        display_lesson['subject_name'] = Subject.query.get(lesson['lesson'].subject_id).subject_name
        display_lesson['tutor_name'] = Tutor.query.get(lesson['lesson'].tutor_id).name
        display_lesson['student_names'] = [f"{student.FirstName} {student.LastName}" for student in lesson['lesson'].students]
        display_lesson['price'] = lesson['lesson'].price
        price_adjustment_id = lesson['lesson'].price_adjustment_id
        price_adjustment = PriceAdjustment.query.get(price_adjustment_id)
        discount = price_adjustment.value if price_adjustment else 0
        display_lesson['discount'] = f"{discount * 100}%"
        display_lesson['final_price'] = lesson['lesson'].final_price
        total_fp += display_lesson['final_price']
        start_datetime = datetime.combine(date.today(), lesson['lesson'].start_time)
        end_datetime = datetime.combine(date.today(), lesson['lesson'].end_time)
        duration_seconds = (end_datetime - start_datetime).total_seconds()
        duration_hours = duration_seconds / 3600
        display_lesson['duration_hours'] = round(duration_hours, 2)
        display_lesson['final_price'] = display_lesson['price'] * display_lesson['duration_hours'] * (1 - discount)
        if has_occured:
            tutor_id = lesson['lesson'].tutor_id
            tutor = Tutor.query.get(tutor_id)
            user_id = tutor.user_id
            user = User.query.get(user_id)
            paygrade = Paygrade.query.get(user.paygrade_id)
            
            tutor_payment = paygrade.value * duration_hours
            display_lesson['tutor_payment'] = tutor_payment
            display_lesson['brutto'] = round_to_nearest_five_cents(lesson['lesson'].final_price - tutor_payment)
        else:
            display_lesson['tutor_payment'] = 0
            display_lesson['brutto'] = display_lesson['final_price']
        total_profit += display_lesson['brutto']
        display_lessons.append(display_lesson)
    total_profit = round_to_nearest_five_cents(total_profit)
    return render_template('admin_financess.html', lessons=display_lessons, default_from_date=from_date.strftime('%Y-%m-%d'), default_end_date=end_date.strftime('%Y-%m-%d'), total_profit=total_profit, total_fp=total_fp)

@app.route('/admin/finances/families', methods=['GET', 'POST'])
@login_required
@admin_required
def finances_families():
    families = Family.query.all()
    lessons_grouped_by_family = {}
    selected_family_id = request.form.get('family_id')
    from_date = request.form.get('from_date')
    end_date = request.form.get('end_date')
    display_lessons = []
    total = 0
    if request.method == 'POST':
        if selected_family_id:
            if selected_family_id == "Alle":
                lessons = get_lessons_in_range(from_date, end_date, None, None, None)
            else:
                lessons = get_lessons_in_range(from_date, end_date, None, int(selected_family_id), None)
            for lesson_detail in lessons:
                
                lesson = lesson_detail['lesson']
                start_time = datetime.combine(lesson.date, lesson.start_time)
                end_datetime = datetime.combine(lesson.date, lesson.end_time)
                duration_timedelta = end_datetime - start_time
                duration_hours = duration_timedelta.seconds / 3600
                total_students = lesson.students.count()
                if total_students == 0:
                    price_per_student = lesson.price
                    final_price_per_student = lesson.final_price
                else:
                    price_per_student = lesson.price / total_students
                    final_price_per_student = lesson.final_price / total_students
                    final_price_per_student = round_to_nearest_five_cents(final_price_per_student)
                for student in lesson.students:
                    if selected_family_id == "Alle" or student.family_id == int(selected_family_id):
                        family_name = Family.query.get(student.family_id).name
                        total += final_price_per_student
                        price_adjustment_id = lesson.price_adjustment_id
                        price_adjustment = PriceAdjustment.query.get(price_adjustment_id)
                        discount = price_adjustment.value if price_adjustment else 0
                        #convert date to dd/mm/yyyy
                        lesson_date = lesson.date.strftime('%d/%m/%Y')
                        part_lesson = {
                            'date' : lesson_date,
                            'subject_name' : Subject.query.get(lesson.subject_id).subject_name,
                            'student_name' : f"{student.FirstName} {student.LastName} ({family_name})",
                            'price' : price_per_student,
                            'duration_hours' : round(duration_hours, 2),
                            'discount' : f"{discount * 100}%",
                            'final_price' : final_price_per_student
                        }
                        if family_name not in lessons_grouped_by_family:
                            lessons_grouped_by_family[family_name] = []
                        lessons_grouped_by_family[family_name].append(part_lesson)
    
    # Sort the lessons by family name
    sorted_lessons = sorted(lessons_grouped_by_family.items(), key=lambda x: x[0])
    
    for family_name, lessons in sorted_lessons:
        display_lessons.extend(lessons)
    
    total = round_to_nearest_five_cents(total)
    return render_template('admin_finances_families.html', families=families, lessons=display_lessons, selected_family_id=selected_family_id, default_from_date=from_date, default_end_date=end_date, total=total)

from flask import current_app


@app.route('/admin/finances/tutors', methods=['GET', 'POST'])
@login_required
@admin_required
def finances_tutors():
    tutors = Tutor.query.all()
    lessons_grouped_by_tutor = {}
    selected_tutor_id = request.form.get('tutor_id')
    from_date = request.form.get('from_date')
    end_date = request.form.get('end_date')
    display_lessons = []
    if request.method == 'POST':
        if selected_tutor_id:
            if selected_tutor_id == "Alle":
                lessons = get_lessons_in_range(from_date, end_date, None, None, None)
            else:
                lessons = get_lessons_in_range(from_date, end_date, None, None, int(selected_tutor_id))
            for lesson_detail in lessons:
                
                lesson = lesson_detail['lesson']
                tutor_id = lesson.tutor_id
                has_occured = lesson.has_occured
                tutor_paygrade = Paygrade.query.filter_by(id=User.query.get(Tutor.query.get(lesson.tutor_id).user_id).paygrade_id).first()
                start_time = datetime.combine(lesson.date, lesson.start_time)
                end_datetime = datetime.combine(lesson.date, lesson.end_time)
                duration_timedelta = end_datetime - start_time
                duration_hours = duration_timedelta.seconds / 3600
                if has_occured:
                    tutor_payment = int(tutor_paygrade.value * duration_hours)
                else:
                    tutor_payment = 0
                subject_name = Subject.query.get(lesson.subject_id).subject_name
                student_names = [f"{student.FirstName} {student.LastName}" for student in lesson.students]
                #convert date to dd/mm/yyyy
                lesson_date = lesson.date.strftime('%d/%m/%Y')
                display_lesson = {
                    'date' : lesson_date,
                    'tutor' : Tutor.query.get(lesson.tutor_id).name,
                    'subject_name' : subject_name,
                    'student_names' : student_names,
                    'duration_hours' : round(duration_hours, 2),
                    'tutor_payment' : tutor_payment
                }
                if tutor_id not in lessons_grouped_by_tutor:
                    lessons_grouped_by_tutor[tutor_id] = []
                lessons_grouped_by_tutor[tutor_id].append(display_lesson)
    sorted_lessons = sorted(lessons_grouped_by_tutor.items(), key=lambda x: Tutor.query.get(x[0]).name)
    for tutor_id, lessons in sorted_lessons:
        display_lessons.extend(lessons)
    
    return render_template('admin_finances_tutors.html', tutors=tutors, lessons=display_lessons, selected_tutor_id=selected_tutor_id, default_from_date=from_date, default_end_date=end_date)


@app.route('/tutors/finances', methods=['GET', 'POST'])
@login_required
@tutor_required
def tutor_finances():
    tutor = Tutor.query.filter_by(user_id=current_user.id).first()
    from_date = request.form.get('from_date')
    end_date = request.form.get('end_date')
    display_lessons = []
    if request.method == 'POST':
        lessons = get_lessons_in_range(from_date, end_date, None, None, tutor.tutor_id)
        tutor_paygrade = Paygrade.query.filter_by(id=User.query.get(tutor.user_id).paygrade_id).first()
        for lesson_detail in lessons:
            lesson = lesson_detail['lesson']
            start_time = datetime.combine(lesson.date, lesson.start_time)
            end_datetime = datetime.combine(lesson.date, lesson.end_time)
            duration_timedelta = end_datetime - start_time
            duration_hours = duration_timedelta.seconds / 3600
            tutor_payment = int(tutor_paygrade.value * duration_hours)
            subject_name = Subject.query.get(lesson.subject_id).subject_name
            student_names = [f"{student.FirstName} {student.LastName}" for student in lesson.students]
            display_lesson = {
                'date' : lesson.date,
                'subject_name' : subject_name,
                'student_names' : student_names,
                'duration_hours' : duration_hours,
                'tutor_payment' : tutor_payment
            }
            display_lessons.append(display_lesson)
    return render_template('tutor_finances.html', lessons=display_lessons, default_from_date=from_date, default_end_date=end_date)


from flask import send_file
from pdf_generator import PDFGenerator

@app.route('/admin/finances/pdf')
@login_required
@admin_required
def download_finances_pdf():
    from_date = request.args.get('from_date')
    end_date = request.args.get('end_date')
    display_lessons = []
    total = 0
    total_fp = 0
    lessons = get_lessons_in_range(from_date, end_date, None, None, None)
    tutors = {lesson['lesson'].tutor_id: Tutor.query.get(lesson['lesson'].tutor_id) for lesson in lessons}
    for lesson in lessons:
        display_lesson = {}
        has_occured = lesson['lesson'].has_occured
        lesson_date = lesson['lesson'].date.strftime('%d/%m/%Y')
        display_lesson['Datum'] = lesson_date
        display_lesson['Fach'] = Subject.query.get(lesson['lesson'].subject_id).subject_name
        display_lesson['Tutor'] = Tutor.query.get(lesson['lesson'].tutor_id).name
        display_lesson['Schüler'] = ', '.join([f"{student.FirstName} {student.LastName}" for student in lesson['lesson'].students])
        display_lesson['Preis'] = lesson['lesson'].price
        price_adjustment_id = lesson['lesson'].price_adjustment_id
        price_adjustment = PriceAdjustment.query.get(price_adjustment_id)
        discount = price_adjustment.value if price_adjustment else 0
        display_lesson['Rabatt'] = f"{discount * 100}%"
        display_lesson['Endpreis'] = lesson['lesson'].final_price
        total_fp += display_lesson['Endpreis']
        if has_occured:
            tutor_id = lesson['lesson'].tutor_id
            tutor = tutors[tutor_id]
            user_id = tutor.user_id
            user = User.query.get(user_id)
            paygrade = Paygrade.query.get(user.paygrade_id)
            start_datetime = datetime.combine(date.today(), lesson['lesson'].start_time)
            end_datetime = datetime.combine(date.today(), lesson['lesson'].end_time)
            duration_seconds = (end_datetime - start_datetime).total_seconds()
            duration_hours = duration_seconds / 3600
            tutor_payment = paygrade.value * duration_hours
            display_lesson['Tutorlohn'] = tutor_payment
            display_lesson['Brutto'] = lesson['lesson'].final_price - tutor_payment
        else:
            display_lesson['Tutorlohn'] = 0
            display_lesson['Brutto'] = display_lesson['Endpreis']
        total += display_lesson['Brutto']
        display_lessons.append(display_lesson)
    total = round_to_nearest_five_cents(total)
    pdf_title = f"Finanzübersicht ({from_date} - {end_date})"
    headers = ['Datum', 'Fach', 'Schüler', 'Tutor', 'Preis', 'Rabatt', 'Endpreis', 'Tutorlohn', 'Brutto']
    pdf_filename = f"finances_{from_date}_{end_date}.pdf"
    pdf_path = os.path.join(current_app.root_path, 'static', 'pdfs', pdf_filename)
    pdf = PDFGenerator()
    pdf.generate_landscape_pdf(pdf_path, pdf_title, display_lessons, headers, total_fp, total)
    return send_file(pdf_path, as_attachment=True, download_name=pdf_filename)


@app.route('/admin/finances/families/pdf')
@login_required
@admin_required
def download_family_finances_pdf():
    selected_family_id = request.args.get('family_id')
    family = Family.query.get(selected_family_id)
    lessons_grouped_by_family = {}
    from_date = request.args.get('from_date')
    end_date = request.args.get('end_date')

    display_lessons = []
    if selected_family_id == "Alle":
        lessons = get_lessons_in_range(from_date, end_date, None, None, None)
    else:
        lessons = get_lessons_in_range(from_date, end_date, None, int(selected_family_id), None)
    total = 0
    for lesson_detail in lessons:
        lesson = lesson_detail['lesson']
        total_students = lesson.students.count()
        if total_students == 0:
            price_per_student = lesson.price
            final_price_per_student = lesson.final_price
        else:
            price_per_student = lesson.price / total_students
            final_price_per_student = lesson.final_price / total_students
        start_time = datetime.combine(lesson.date, lesson.start_time)
        end_datetime = datetime.combine(lesson.date, lesson.end_time)
        duration_timedelta = end_datetime - start_time
        duration_hours = duration_timedelta.seconds / 3600
        for student in lesson.students:
            if selected_family_id == "Alle" or student.family_id == int(selected_family_id):
                family_name = Family.query.get(student.family_id).name
                price_adjustment_id = lesson.price_adjustment_id
                price_adjustment = PriceAdjustment.query.get(price_adjustment_id)
                discount = price_adjustment.value if price_adjustment else 0
                total += final_price_per_student
                #convert date to dd/mm/yyyy
                lesson_date = lesson.date.strftime('%d/%m/%Y')

                part_lesson = {
                    'Datum' : lesson_date,
                    'Fach' : Subject.query.get(lesson.subject_id).subject_name,
                    'Schüler' : f"{student.FirstName} {student.LastName} ({family_name})",
                    'Preis': f"{price_per_student:.2f}",
                    'Dauer' : f"{duration_hours:.2f} Stunden", # 'Dauer' : '2.5 Stunden
                    'Rabatt' : f"{discount * 100}%",
                    'Endpreis': f"{final_price_per_student:.2f}"
                }
                if family_name not in lessons_grouped_by_family:
                    lessons_grouped_by_family[family_name] = []
                lessons_grouped_by_family[family_name].append(part_lesson)
    
    # Sort the lessons by family name
    sorted_lessons = sorted(lessons_grouped_by_family.items(), key=lambda x: x[0])
    
    for family_name, lessons in sorted_lessons:
        display_lessons.extend(lessons)

    if selected_family_id == "Alle":
        pdf_title = f"Finanzübersicht für alle Familien ({from_date} - {end_date})"
    else:
        pdf_title = f"Finanzübersicht für Familie {family.name} ({from_date} - {end_date})"
    headers = ['Datum', 'Fach', 'Schüler', 'Preis', 'Dauer', 'Rabatt', 'Endpreis']
    if selected_family_id == "Alle":
        pdf_filename = f"family_finances_all_{from_date}_{end_date}.pdf"
    else:
        pdf_filename = f"family_finances_{family.name}_{from_date}_{end_date}.pdf"
    pdf_path = os.path.join(current_app.root_path, 'static', 'pdfs', pdf_filename)

    pdf = PDFGenerator()
    pdf.generate_pdf(pdf_path, pdf_title, display_lessons, headers, total)

    return send_file(pdf_path, as_attachment=True, download_name=pdf_filename)
    
    

@app.route('/admin/finances/tutors/pdf')
@login_required
@admin_required
def download_tutor_finances_pdf():
    selected_tutor_id = request.args.get('tutor_id')
    tutor = Tutor.query.get(selected_tutor_id)
    from_date = request.args.get('from_date')
    end_date = request.args.get('end_date')
    lessons_grouped_by_tutor = {}
    total = 0
    if selected_tutor_id == "Alle":
        lessons = get_lessons_in_range(from_date, end_date, None, None, None)
    else:
        lessons = get_lessons_in_range(from_date, end_date, None, None, int(selected_tutor_id))

    
    for lesson_detail in lessons:
        lesson = lesson_detail['lesson']
        has_occured = lesson.has_occured
        start_time = datetime.combine(lesson.date, lesson.start_time)
        end_datetime = datetime.combine(lesson.date, lesson.end_time)
        duration_timedelta = end_datetime - start_time
        duration_hours = duration_timedelta.seconds / 3600
        tutor = Tutor.query.get(lesson.tutor_id)
        tutor_paygrade = Paygrade.query.filter_by(id=User.query.get(tutor.user_id).paygrade_id).first()
        if has_occured:
            tutor_payment = int(tutor_paygrade.value * duration_hours)
            total += tutor_payment
        else:
            tutor_payment = 0
            
        subject_name = Subject.query.get(lesson.subject_id).subject_name
        student_names = [f"{student.FirstName} {student.LastName}" for student in lesson.students]
        student_names = ', '.join(student_names)
        #format time to dd/mm/yyyy
        lesson_date = lesson.date.strftime('%d/%m/%Y')
        display_lesson = {
            'Datum' : lesson_date,
            'Tutor' : Tutor.query.get(lesson.tutor_id).name,
            'Fach' : subject_name,
            'Schüler' : student_names,
            'Dauer' : f"{duration_hours:.2f} Stunden",
            'Tutorlohn' : f"{tutor_payment:.2f}"
        }
        if tutor.tutor_id not in lessons_grouped_by_tutor:
            lessons_grouped_by_tutor[tutor.tutor_id] = []
        lessons_grouped_by_tutor[tutor.tutor_id].append(display_lesson)
    sorted_lessons = sorted(lessons_grouped_by_tutor.items(), key=lambda x: Tutor.query.get(x[0]).name)
    
    
    if selected_tutor_id == "Alle":
        pdf_title = f"Finanzübersicht für alle Tutoren ({from_date} - {end_date})"
    else:
        pdf_title = f"Finanzübersicht für Tutor {tutor.name} ({from_date} - {end_date})"
    headers = ['Datum', 'Tutor', 'Fach', 'Schüler', 'Dauer', 'Tutorlohn']
    if selected_tutor_id == "Alle":
        pdf_filename = f"tutor_finances_all_{from_date}_{end_date}.pdf"
    else:
        pdf_filename = f"tutor_finances_{tutor.name}_{from_date}_{end_date}.pdf"
    
    pdf_path = os.path.join(current_app.root_path, 'static', 'pdfs', pdf_filename)

    pdf = PDFGenerator()
    #pdf.generate_pdf(pdf_path, pdf_title, display_lessons, headers, total)
    subtotal = 0
    pdf.generate_tutor_l_pdf(pdf_path, pdf_title, sorted_lessons, headers, total)

    return send_file(pdf_path, as_attachment=True, download_name=pdf_filename)

        

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from reportlab.lib import colors

import os

@app.route('/admin/finances/create_pdf', methods=['POST'])
@login_required
@admin_required
def create_pdf():
    data = request.get_json()

    lessons = data['lessons']
    finances = data['finances']
    total_profit = data['total_profit']
    others = data.get('others', [])
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(dir_path, "finances_{}.pdf".format(datetime.now().strftime("%Y%m%d%H%M%S")))
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph('Finanz-Bericht', styles['Title']))

    # Lessons table
    elements.append(Paragraph('Nachhilfestunden', styles['Heading2']))
    lessons_data = [['Datum', 'Fach', 'Tutor (T.)', 'Schüler', 'Preis', 'Rabatt (%)', 'P. inkl. %', 'T. Lohn', 'Brutto']] + \
            [[Paragraph(datetime.strptime(lesson['date'], '%Y-%m-%d').strftime('%d/%m/%Y'), styles['BodyText']),  # Convert date to dd/mm/yyyy format
              Paragraph(lesson['subject'], styles['BodyText']), 
              Paragraph(lesson['tutor_name'], styles['BodyText']), 
              Paragraph(lesson['student_name'], styles['BodyText']), 
              Paragraph(lesson['price'], styles['BodyText']), 
              Paragraph(lesson['discount'], styles['BodyText']), 
              Paragraph(lesson['final_price'], styles['BodyText']), 
              Paragraph(lesson['tutor_payment'], styles['BodyText']), 
              Paragraph(lesson['gross_wage'], styles['BodyText'])] for lesson in lessons]
    lessons_table = Table(lessons_data, rowHeights=30, colWidths=[70, 70, 70, 120, 40, 80, 50, 50, 45])  # Increase row height
    lessons_table.setStyle(TableStyle([
    ('GRID', (0,0), (-1,-1), 1, colors.black),
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey)
    ]))
    elements.append(lessons_table)

    # Finances table
    elements.append(Paragraph('Einschreibegebühr', styles['Heading2']))
    finances_data = [['Beschreibung', 'Preis']] + \
                    [[finance['description'], finance['amount']] for finance in finances]
    finances_table = Table(finances_data)
    finances_table.setStyle(TableStyle([
    ('GRID', (0,0), (-1,-1), 1, colors.black),
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey)
    ]))
    elements.append(finances_table)

    # Others table
    if others:
        elements.append(Paragraph('Others', styles['Heading2']))
        others_data = [['Description', 'Amount']] + \
                    [[other['description'], other['amount']] for other in others]
        others_table = Table(others_data)
        others_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey)
        ]))
        elements.append(others_table)

    # Total profit
    elements.append(Paragraph('Saldo', styles['Heading2']))
    elements.append(Paragraph(str(total_profit), styles['BodyText']))

    # Generate PDF
    doc.build(elements)

    return send_file(filename, as_attachment=True)

@app.route('/admin/tutors/create_pdf', methods=['POST'])
@login_required
@admin_required
def create_tutor_pdf():
    data = request.get_json()

    lessons = data['lessons']
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(dir_path, "finances_{}.pdf".format(datetime.now().strftime("%Y%m%d%H%M%S")))
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph('Tutor-Bericht', styles['Title']))

    # Lessons table
    elements.append(Paragraph('Nachhilfestunden', styles['Heading2']))
    lessons_data = [['Datum', 'Fach', 'Tutor', 'Schüler', 'Tutorzahlung']] + \
            [[Paragraph(datetime.strptime(lesson['date'], '%Y-%m-%d').strftime('%d/%m/%Y'), styles['BodyText']),  # Convert date to dd/mm/yyyy format
              Paragraph(lesson['subject'], styles['BodyText']), 
              Paragraph(lesson['tutor_name'], styles['BodyText']), 
              Paragraph(lesson['student_name'], styles['BodyText']), 
              Paragraph(lesson['tutor_payment'], styles['BodyText'])] for lesson in lessons]
    lessons_table = Table(lessons_data, rowHeights=30, colWidths=[70, 70, 70, 120, 70])  # Increase row height
    lessons_table.setStyle(TableStyle([
    ('GRID', (0,0), (-1,-1), 1, colors.black),
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey)
    ]))
    elements.append(lessons_table)

    # Total tutor payment
    total_tutor_payment = sum(float(lesson['tutor_payment']) for lesson in lessons)
    elements.append(Paragraph('Gesamt Tutorzahlung', styles['Heading2']))
    elements.append(Paragraph(str(total_tutor_payment), styles['BodyText']))

    # Generate PDF
    doc.build(elements)

    return send_file(filename, as_attachment=True)

@app.route('/update_entrance_fee', methods=['POST'])
def update_entrance_fee():
    ENTRANCE_FEE_AMOUNT = 50
    family_id = request.form.get('family_id')
    has_paid = request.form.get('has_paid') == 'true'
    family = Family.query.get(family_id)

    # If the family has already paid the entrance fee, return early
    if family.entrance_fee and has_paid:
        return jsonify(success=True)

    family.entrance_fee = has_paid
    if has_paid:
        finance = Finance(amount=ENTRANCE_FEE_AMOUNT, description=f'{family.name} Einschreibegebühr', family_id=family_id)
        db.session.add(finance)
    db.session.commit()
    return jsonify(success=True)


@app.route('/lesson/<int:lesson_id>')
@login_required
def lesson_detail(lesson_id):
    
    user = User.query.get(current_user.id)
    lesson = Lesson.query.get(lesson_id)
    tutor_id = lesson.tutor_id
    tutor = Tutor.query.get(tutor_id)
    impostor = Tutor.query.filter_by(user_id=current_user.id).first()
    if user.role.name == 'tutor':
        if impostor != tutor:
            return redirect(url_for('error_page'))
    if lesson is None:
        if user.role.name == 'admin':
            return redirect(url_for('admin_dashboard'))
        if user.role.name == 'tutor':
            return redirect(url_for('tutor_dashboard', user_id=user.id))

    is_admin = user.role.name == 'admin'
    is_tutor = user.role.name == 'tutor'
    subject = Subject.query.get(lesson.subject_id)
    schooltypes = SchoolType.query.all()
    tutors = Tutor.query.all()
    notes = Note.query.filter_by(lesson_id=lesson_id).all()
    students = lesson.students.all()
    price_adjustment = PriceAdjustment.query.all()
    return render_template('lesson_detail.html', lesson=lesson, is_admin=is_admin, schooltypes=schooltypes, subject=subject, tutor=tutor, tutoren=tutors, notes=notes, students=students, price_adjustments=price_adjustment, is_tutor=is_tutor)

from datetime import datetime

@app.route('/lesson/<int:lesson_id>/update', methods=['POST'])
@login_required
def update_lesson(lesson_id):
    lesson = Lesson.query.get(lesson_id)
    if lesson is None:
        return redirect(url_for('modify_lessons'))

    # Update the lesson details
    subject = Subject.query.filter_by(subject_id=request.form['subject']).one()
    lesson.subject_id = subject.subject_id
    lesson.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    start_time = request.form['start_time']
    if len(start_time) == 5:  # 'HH:MM' format
        start_time += ':00'  # Add seconds
    lesson.start_time = datetime.strptime(start_time, '%H:%M:%S').time()

    end_time = request.form['end_time']
    if len(end_time) == 5:  # 'HH:MM' format
        end_time += ':00'  # Add seconds
    lesson.end_time = datetime.strptime(end_time, '%H:%M:%S').time()

    # Check if 'tutor_id', 'price', 'price_adjustment_id', 'final_price' and 'has_occured' fields are in the form data
    if 'tutor_id' in request.form:
        tutor_id = request.form['tutor_id']
        lesson.tutor_id = tutor_id
    if 'price' in request.form:
        lesson.price = float(request.form['price'])
    if 'price_adjustment' in request.form:
        try:
            # Try to get the PriceAdjustment record with the given ID
            price_adjustment_id = int(request.form['price_adjustment'])
            price_adjustment = PriceAdjustment.query.get(price_adjustment_id)
            if price_adjustment is not None:
                lesson.price_adjustment_id = price_adjustment.id
            else:
                print(f"No PriceAdjustment record found with ID {price_adjustment_id}")
        except ValueError:
            print(f"Invalid price_adjustment: {request.form['price_adjustment']}")
    if 'final_price' in request.form:
        lesson.final_price = float(request.form['final_price'])
    else:
        price_adjustment = PriceAdjustment.query.get(lesson.price_adjustment_id)
        lesson.final_price = lesson.price * (1 - price_adjustment.value) if price_adjustment else lesson.price
    if request.form.get('has_occured') is not None:
        lesson.has_occured = True
    else:
        lesson.has_occured = False

    updated_notes_content = request.form['notes']
    note = Note.query.filter_by(lesson_id=lesson_id).first()
    if note:
        note.content = updated_notes_content 

    else:
        note = Note(lesson_id = lesson_id, content = updated_notes_content)
        db.session.add(note)

    db.session.commit()

    return redirect(url_for('lesson_detail', lesson_id=lesson.lesson_id))

@app.route('/admin/find_tutors', methods=['GET'])
@login_required
@admin_required
def query_tutors():
    return 200

@app.route('/delete_family/<int:family_id>', methods=['POST'])
@login_required
@admin_required
def delete_family(family_id):
    family = Family.query.get(family_id)
    students_in_family = Student.query.filter_by(family_id=family_id).first()
    if family and not students_in_family:
        # Delete or update all finance records related to the family
        Finance.query.filter_by(family_id=family_id).delete()
        db.session.delete(family)
        db.session.commit()
    return redirect(url_for('modify_family'))


@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    student = Student.query.get(student_id)
    if student:
        # Remove the student from all lessons
        for lesson in student.enrolled_lessons:
            lesson.students.remove(student)
        
        # Delete all report cards related to the student
        ReportCard.query.filter_by(student_id=student_id).delete()

        # Remove the student from the family
        # Note: This assumes that a family can exist without students. If this is not the case, you might want to delete the family as well.
        student.family_id = None

        # Remove the student's school type
        # Note: This assumes that a school type can exist without students. If this is not the case, you might want to delete the school type as well.
        student.schooltype_id = None

        db.session.delete(student)
        db.session.commit()
    return redirect(url_for('modify_family'))



if __name__ == '__main__':
    app.run(debug=True)
    
