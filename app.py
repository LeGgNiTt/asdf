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



def create_admin_user(username, password):
    with app.app_context():
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin')
            db.session.add(admin_role)
            db.session.commit()

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User.query.filter_by(username=username).first()
        if user is not None:
            print(f"User '{username}' already exists. No new user created.")
            return

        admin_user = User(username=username, password_hash=hashed_password, role_id=admin_role.id, paygrade_id=1)
        db.session.add(admin_user)
        db.session.commit()
        print(f"Admin user '{username}'  created.")

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

def create_user_with_role(username, password, role_name, paygrade=1):
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
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    for day in days:
        existing_day = Weekday.query.filter_by(weekday_name=day).first()
        if not existing_day:
            new_day = Weekday(weekday_name=day)
            db.session.add(new_day)
    db.session.commit()


def calculate_monthly_income():
    monthly_income = 0
    return monthly_income
def get_lessons_count():
    lesson_count = 0
    return lesson_count
def get_detailed_statistics():
    detailed_statistics = 0
    return detailed_statistics

def get_lessons_in_range(from_date, end_date, school_type_id=None, family_id=None, tutor_id=None):
    lessons = Lesson.query.filter(Lesson.date.between(from_date, end_date))
    if school_type_id:
        subject_ids = [subject.subject_id for subject in Subject.query.filter_by(schooltype_id=school_type_id)]
        lessons = lessons.filter(Lesson.subject_id.in_(subject_ids))
    if family_id:
        lessons = lessons.filter(Student.family_id == family_id)
    if tutor_id:
        lessons = lessons.filter(Lesson.tutor_id == tutor_id)
    return lessons.all()


app = Flask(__name__)
# Database configuration and initialization
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:rootroot@localhost/showcase'
app.config['SECRET_KEY'] = 'development'
db.init_app(app)
with app.app_context():
    db.create_all()

migrate = Migrate(app, db)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)




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

def is_tutor_available(tutor, date, start_time, end_time):
    # Convert date to weekday (assuming 'date' is a datetime object)
    weekday_name = date.strftime("%A")

    # Check availability on the given weekday
    availabilities = TutorAvailability.query.filter(
        TutorAvailability.tutor_id == tutor.tutor_id,
        TutorAvailability.weekday.has(Weekday.weekday_name == weekday_name)
    ).all()

    for availability in availabilities:
        # Convert start_time and end_time to time objects if they are not already
        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, '%H:%M').time()
        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time, '%H:%M').time()

        if availability.start_time <= start_time and availability.end_time >= end_time:
            # Check for conflicting lessons
            conflicting_lesson = Lesson.query.filter(
                Lesson.tutor_id == tutor.tutor_id,
                Lesson.date == date,
                Lesson.start_time < end_time,
                Lesson.end_time > start_time
            ).first()

            if not conflicting_lesson:
                return True  # Tutor is available

    return False  # Tutor is not available




@app.route('/api/tutors/<int:subject_id>/<date>/<start_time>/<end_time>', methods=['GET'])
def get_tutors_for_subject_and_time(subject_id, date, start_time, end_time):
    start_time = datetime.strptime(start_time, '%H:%M').time()
    end_time = datetime.strptime(end_time, '%H:%M').time()
    date = datetime.strptime(date, '%Y-%m-%d').date()

    tutors = Tutor.query.join(TutorSubject).filter(TutorSubject.subject_id == subject_id).all()

    tutor_data = []
    for tutor in tutors:
        availability = is_tutor_available(tutor, date, start_time, end_time)
        status = "available" if availability else "unavailable"
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
    monthly_income = calculate_monthly_income()
    lessons_count = get_lessons_count()
    lessons = Lesson.query.all()

    # Format lessons for display
    formatted_lessons = []
    for lesson in lessons:
        tutor_name = Tutor.query.filter_by(tutor_id=lesson.tutor_id).first().name
        students = lesson.students
        student_name = [f"{student.FirstName} {student.LastName}" for student in students]
        subject_name = Subject.query.filter_by(subject_id=lesson.subject_id).first().subject_name

        start_datetime = datetime.combine(lesson.date, lesson.start_time)
        end_datetime = datetime.combine(lesson.date, lesson.end_time)

        formatted_lessons.append({
            'id': lesson.lesson_id, 
            'title': subject_name,
            'start': start_datetime.isoformat(),
            'end': end_datetime.isoformat(),
            'tutor': tutor_name,
            'student': student_name
        })

    return render_template('admin_dashboard.html', monthly_income_summary=monthly_income, lessons_count_summary=lessons_count, lessons=formatted_lessons)

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

@app.route('/tutor/change_password', methods=['GET', 'POST'])
@login_required
@tutor_required
def change_poassword():
    user_id = current_user.id
    user = User.query.get(user_id)
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        repeat_password = request.form['repeat_password']
        
        
        # Check if the old password matches the user's current password
        if user.check_password(old_password):
            # Check if the new password and repeat password match
            if new_password == repeat_password:
                password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                user.password_hash = password


                db.session.commit()
                flash('Password updated successfully', 'success')
            else:
                flash('New password and repeat password do not match', 'danger')
        else:
            flash('Incorrect old password', 'danger')
        
        return redirect(url_for('tutor_profile'))
    
    return render_template('change_password.html', user=user)
    

@app.route('/tutor/view_students', methods=['GET', 'POST'])
@login_required
@tutor_required
def view_students():
    user_id = current_user.id
    tutor_id = Tutor.query.filter_by(user_id=user_id).first().tutor_id
    lessons = Lesson.query.filter_by(tutor_id=tutor_id).all()
    students = []
    for lesson in lessons:
        for student_lesson in lesson.students:
            student = Student.query.filter_by(StudentID=student_lesson.StudentID).first()
            students.append(student)
    return render_template('view_students.html', students=students)




@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get(user_id)
    if request.method == 'POST':
        return True
    return True


@app.route('/student/<id>')
def student(id):
    # Fetch the student with the given ID from the database
    student = Student.query.get(id)

    # Check if the student exists
    if student is None:
        # If the student does not exist, redirect to the home page
        return redirect(url_for('home'))

    # Fetch the tutor associated with the current user
    tutor = Tutor.query.filter_by(user_id=current_user.id).first()

    # Check if the tutor exists
    if tutor is None:
        # If the tutor does not exist, redirect to the home page
        return redirect(url_for('home'))

    # Check if there exists a lesson with student_id equal to <id> and tutor_id equal to the fetched tutor's ID
    lesson = Lesson.query.filter_by(student_id=id, tutor_id=tutor.tutor_id).first()
    if lesson is None:
        # If no such lesson exists, redirect to the home page
        return redirect(url_for('home'))

    # Fetch all notes associated with the student from the database
    notes = Note.query.filter_by(student_id=id).all()

    # Render the 'student.html' template and pass the student data and the notes to it
    return render_template('student.html', student=student, notes=notes)



from datetime import datetime

@app.route('/api/lessons')
@login_required
@admin_required
def get_lessons():
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

        for student_lesson in lesson.students:
            student = Student.query.filter_by(StudentID=student_lesson.StudentID).first()

            lessons_data.append({
                'id': lesson.lesson_id,
                'title': f"{subject.subject_name} - {student.LastName} - {tutor.name}",
                'start': start_datetime.isoformat(),
                'end': end_datetime.isoformat(),
                'description': f"Tutor: {tutor.name}, Student: {student.FirstName} {student.LastName}",
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
    lessons = (db.session.query(Lesson, Subject.subject_name)
               .join(Subject, Lesson.subject_id == Subject.subject_id)
               .filter(Lesson.tutor_id == tutor.tutor_id)
               .all())

    # Create a list of lesson dictionaries
    lesson_info = [{
        'date': lesson_obj.date,
        'subject': subject_name,
        'notes': [{'date': note.date, 'content': note.content} for note in lesson_obj.notes],
        'has_occured': lesson_obj.has_occured,
        'id': lesson_obj.lesson_id
    } for lesson_obj, subject_name in lessons]

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
def delete_lesson():
    pass

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
        db.session.commit()
        return redirect(url_for('modify_family'))
    return render_template('edit_student.html', student=student, schooltypes=schooltypes)

from datetime import datetime, timedelta

@app.route('/modify_lessons', methods=['GET', 'POST'])
@login_required
@admin_required
def modify_lessons():
    # Fetch all lessons
    lessons = Lesson.query.all()

    # Format lessons for display
    formatted_lessons = []
    for lesson in lessons:
        today = datetime.today().strftime('%Y-%m-%d')
        # Fetch tutor, student, and subject names using separate queries
        tutor_name = Tutor.query.filter_by(tutor_id=lesson.tutor_id).first().name
        students = lesson.students
        student_names = [f"{student.FirstName} {student.LastName}" for student in students]
        subject_name = Subject.query.filter_by(subject_id=lesson.subject_id).first().subject_name

        formatted_lessons.append({
            'lesson_id': lesson.lesson_id,
            'date': lesson.date.strftime('%Y-%m-%d'),
            'start_time': lesson.start_time.strftime('%H:%M'),
            'end_time': lesson.end_time.strftime('%H:%M'),
            'tutor_name': tutor_name,
            'student_name': student_names,
            'subject_name': subject_name,
            'has_occurred': lesson.has_occured,
            'notes': ', '.join(note.content for note in lesson.notes) if lesson.notes else ''

        })
        if request.method == 'POST':
            from_date_str = request.form.get('from_date')
            to_date_str = request.form.get('to_date')
            schooltype_id = request.form.get('schooltype_id')
            subject_id = request.form.get('subject_id')

            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else None
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else None

            lessons_query = Lesson.query

            if from_date and to_date:
                lessons_query = lessons_query.filter(Lesson.date.between(from_date, to_date))
            elif from_date:
                lessons_query = lessons_query.filter(Lesson.date >= from_date)
            elif to_date:
                lessons_query = lessons_query.filter(Lesson.date <= to_date)

            if schooltype_id:
                lessons_query = lessons_query.filter(Lesson.schooltype_id == schooltype_id)

            if subject_id:
                lessons_query = lessons_query.filter(Lesson.subject_id == subject_id)

            lessons = lessons_query.all()

            formatted_lessons = []
            for lesson in lessons:
                formatted_lessons.append({
                    'lesson_id': lesson.id,
                    'date': lesson.date.strftime('%Y-%m-%d'),
                    'start_time': lesson.start_time.strftime('%H:%M'),
                    'end_time': lesson.end_time.strftime('%H:%M'),
                    'tutor_name': lesson.tutor.user.full_name,
                    'student_name': lesson.student.user.full_name,
                    'subject_name': lesson.subject.subject_name,
                    'has_occurred': lesson.has_occurred,
                    'notes': lesson.notes
                })

            return render_template('modify_lessons.html', lessons=formatted_lessons)

    return render_template('modify_lessons.html', lessons=formatted_lessons)

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



@app.route('/add_lesson', methods=['GET', 'POST'])
@login_required
@admin_required
def add_lesson():
    if request.method == 'POST':
        date = request.form.get('date')
        date = datetime.strptime(date, '%Y-%m-%d').date()
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        tutor_id = request.form.get('tutor_id')
        student_id = request.form.get('student_id')
        subject_id = request.form.get('subject_id')
        price = request.form.get('price')
        regelmaessig = request.form.get('regelmaessig') is not None
        
        price_adjustment_id = request.form.get('price_adjustment_id')
        price_adjustment = PriceAdjustment.query.get(price_adjustment_id)

        adjustment_value = price_adjustment.value
        ferienkurs = request.form.get('ferienkurs') is not None

        student_ids = request.form.getlist('student_ids')
        if ferienkurs == True:
            for i in range(0,5):
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
        if regelmaessig:
            for i in range(4):  # create a lesson for each of the next 4 weeks
                new_lesson = Lesson(
                    date=date + timedelta(weeks=i),
                    start_time=start_time,
                    end_time=end_time,
                    tutor_id=tutor_id,
                    subject_id=subject_id,
                    price=price,
                    price_adjustment_id=price_adjustment_id,
                    final_price=(float(price) - adjustment_value),
                    lesson_type_id=1
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
                final_price= price,
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
                final_price= (float(price) - adjustment_value),
                lesson_type_id = 1
            )
            for student_id in student_ids:
                student = Student.query.get(student_id)
                student.enrolled_lessons.append(new_lesson) # Add the lesson to the student's enrolled lessons
            db.session.add(new_lesson)
            db.session.commit()
            return redirect(url_for('modify_lessons'))

    
    students = Student.query.all()
    price_adjustments = PriceAdjustment.query.all()
    schooltypes = SchoolType.query.all()
    return render_template('add_lesson.html', students=students, price_adjustments=price_adjustments, schooltypes=schooltypes)

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


@app.route('/tutor/edit_tutor', methods=['GET', 'POST'])
@login_required
@tutor_required
def edit_tutor():
    tutor = Tutor.query.filter_by(user_id=current_user.id).first()
    subjects = Subject.query.join(TutorSubject).filter(TutorSubject.tutor_id == tutor.tutor_id).all()
    if request.method == 'POST':
        return False

    return render_template('edit_tutor.html', tutor=tutor, subjects=subjects)


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


@app.route('/tutor/<int:tutor_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def tutor_profil_id(tutor_id):
    tutor = Tutor.query.get(tutor_id)
    return render_template('admin_tutor_profile.html', tutor=tutor)

from datetime import datetime
from flask import request, redirect, url_for, flash, render_template
from datetime import datetime, timedelta

@app.route('/create_tutor_profile', methods=['GET', 'POST'])
@login_required
def create_tutor_profile():
    schooltypes = SchoolType.query.all()
    if request.method == 'POST':
        # Dictionary to hold availability data
        availability_data = {}

        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]:
            for slot in ["1", "2"]:
                start_time = request.form.get(f'{day}_start_{slot}')
                end_time = request.form.get(f'{day}_end_{slot}')
                
                if start_time and end_time:
                    start_time = datetime.strptime(start_time, '%H:%M').time()
                    end_time = datetime.strptime(end_time, '%H:%M').time()
                    # Save these times in the availability_data dictionary
                    if day not in availability_data:
                        availability_data[day] = []
                    availability_data[day].append((start_time, end_time))
        
        # Get the current user's tutor profile or create a new one
        tutor_name = request.form.get('name')
        tutor = Tutor.query.filter_by(user_id=current_user.id).first()
        if not tutor:
            tutor = Tutor(name = tutor_name, user_id = current_user.id)
            db.session.add(tutor)
            db.session.commit()
        
        # Process the availability data
        for day, times in availability_data.items():
            weekday = Weekday.query.filter_by(weekday_name=day.capitalize()).first()
            if not weekday:
                continue  # Skip if the weekday is not found

            for start_time, end_time in times:
                availability = TutorAvailability(
                    tutor_id=tutor.tutor_id,
                    weekday_id=weekday.weekday_id,
                    start_time=start_time,
                    end_time=end_time
                )
                db.session.add(availability)

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

    return render_template('create_tutor_profile.html', schooltypes=schooltypes)

from dateutil.relativedelta import relativedelta

@app.route('/admin/finances', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_finances():
    today = datetime.now()
    from_date = datetime(today.year, today.month, 1)
    end_date = datetime(today.year, today.month, 1) + relativedelta(months=1) - timedelta(days=1)
    school_type = None
    family_id = None
    tutor_id = None
    lessons = get_lessons_in_range(from_date, end_date, school_type, family_id, tutor_id)
    tutors = {lesson.tutor_id: Tutor.query.get(lesson.tutor_id) for lesson in lessons}
    if request.method == 'POST':
        from_date_str = request.form.get('from_date')
        end_date_str = request.form.get('end_date')
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        school_type = request.form.get('school_type')
        family_id = request.form.get('family_id')
        tutor_id = request.form.get('tutor_id')

        # Convert the IDs to integers if they are not None or an empty string
        school_type = int(school_type) if school_type else None
        family_id = int(family_id) if family_id else None
        tutor_id = int(tutor_id) if tutor_id else None

        lessons = get_lessons_in_range(from_date, end_date, school_type, family_id, tutor_id)
        tutors = {lesson.tutor_id: Tutor.query.get(lesson.tutor_id) for lesson in lessons}
    users = {tutor.user_id: User.query.get(tutor.user_id) for tutor in tutors.values()}
    paygrades = Paygrade.query.all()
    schooltypes = SchoolType.query.all()
    families = Family.query.all()
    all_tutors = Tutor.query.all()    
    lesson_schooltypes = {lesson.lesson_id: SchoolType.query.get(Subject.query.get(lesson.subject_id).schooltype_id) for lesson in lessons}
    return render_template('admin_finances.html', lessons=lessons, tutors=tutors, users=users, paygrades=paygrades, schooltypes=schooltypes, families=families, all_tutors=all_tutors, default_from_date=from_date.strftime('%Y-%m-%d'), default_end_date=end_date.strftime('%Y-%m-%d'), submitted_school_type_id=school_type, submitted_family_id=family_id, submitted_tutor_id=tutor_id, lesson_schooltypes=lesson_schooltypes)

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
    subject = Subject.query.get(lesson.subject_id)
    schooltypes = SchoolType.query.all()
    tutors = Tutor.query.all()
    notes = Note.query.filter_by(lesson_id=lesson_id).all()
    students = lesson.students.all()
    price_adjustment = PriceAdjustment.query.all()
    return render_template('lesson_detail.html', lesson=lesson, is_admin=is_admin, schooltypes=schooltypes, subject=subject, tutor=tutor, tutoren=tutors, notes=notes, students=students, price_adjustments=price_adjustment)

from datetime import datetime

@app.route('/lesson/<int:lesson_id>/update', methods=['POST'])
@login_required
def update_lesson(lesson_id):
    lesson = Lesson.query.get(lesson_id)
    if lesson is None:
        return redirect(url_for('modify_lessons'))

    # Update the lesson details
    subject = Subject.query.filter_by(subject_name=request.form['subject']).one()
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
    if request.form.get('has_occured') is not None:
        lesson.has_occured = True
    else:
        lesson.has_occured = False

    db.session.commit()

    return redirect(url_for('lesson_detail', lesson_id=lesson.lesson_id))




if __name__ == '__main__':
    create_admin_user('hansueli', 'V4-guns5')
    app.run(debug=True)
