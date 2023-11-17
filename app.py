# app.py
from models import Tutor, SchoolType, Subject, TutorSubject, Student, Lesson
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, logging, flash
from functools import wraps
from models import db, SchoolType, Student, User, Role, Tutor, Lesson, Subject, Weekday, Availability, TutorSubject
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

def create_admin_user(username, password):
    
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin')
        db.session.add(admin_role)
        db.session.commit()

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User.query.filter_by(username=username).first()
    if user is not None:
        raise ValueError('User already exists')
    
    
    admin_user = User(username=username, password_hash=hashed_password, role_id=admin_role.id)
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

def create_user_with_role(username ,password, role_name):
    role = Role.query.filter_by(name=role_name).first()
    if role:
        new_user = User(username=username, password_hash=bcrypt.generate_password_hash(password).decode('utf-8'), role_id=role.id)
        db.session.add(new_user)
        db.session.commit()
        print(f"User '{username}' created with role '{role_name}'")
    else:
        print(f"Role '{role_name}' does not exist.")

def calculate_monthly_income():
    monthly_income = 0
    return monthly_income
def get_lessons_count():
    lesson_count = 0
    return lesson_count
def get_detailed_statistics():
    detailed_statistics = 0
    return detailed_statistics

app = Flask(__name__)
# Database configuration and initialization
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:rootroot@localhost/showcase'
app.config['SECRET_KEY'] = 'development'
db.init_app(app)
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
                return redirect(url_for('tutor_dashboard'))
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
    return render_template('admin_dashboard.html', monthly_income_summary=monthly_income, lessons_count_summary=lessons_count)

@app.route('/detailed_statistics')
@admin_required
def detailed_statistics():
    detailed_statistics = get_detailed_statistics()
    return render_template('detailed_statistics.html', detailed_statistics=detailed_statistics)

@app.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.role.name != 'admin':  # Check the role name instead of role_id
        flash("You don't have permission to access this page.", 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role_name = request.form['role']

        # Call your create_user_with_role function
        message, success = create_user_with_role(username, password, role_name)
        flash(message, 'success' if success else 'danger')

        if success:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('create_user'))

    return render_template('create_user.html')


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



@app.route('/add_lesson', methods=['GET', 'POST'])
@login_required
@admin_required
def add_lesson():
    if request.method == 'POST':
        # Extract data from form submission
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        tutor_id = request.form.get('tutor_id')
        student_id = request.form.get('student_id')
        subject_id = request.form.get('subject_id')
        
        # Create a new Lesson object
        new_lesson = Lesson(
            date=date,
            start_time=start_time,
            end_time=end_time,
            tutor_id=tutor_id,
            student_id=student_id,
            subject_id=subject_id
        )
        
        # Add to the database
        db.session.add(new_lesson)
        db.session.commit()
        
        # Flash message for successful addition
        flash('Lesson added successfully!', 'success')
        
        # Redirect to the admin_lessons page
        return redirect(url_for('admin_lessons'))
    
    # If GET request, render the form template
    # You need to pass the tutors, students, and subjects to the template
    tutors = Tutor.query.all()
    students = Student.query.all()
    subjects = Subject.query.all()
    return render_template(
        'add_lesson.html', 
        tutors=tutors, 
        students=students, 
        subjects=subjects
    )

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
    if request.method == 'POST':
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            schooltype_id = request.form.get('schooltype_id')
            date_of_birth = request.form.get('date_of_birth')
            preffered_time = request.form.get('preffered_time')
            new_student = Student(FirstName=first_name, LastName=last_name, schooltype_id=schooltype_id, DateOfBirth=date_of_birth, preferred_time=preffered_time, family_id=family_id)
            db.session.add(new_student)
            db.session.commit()
            return redirect(url_for('modify_family'))

    return render_template('add_student_to_F.html')



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        


    app.run(debug=True)
