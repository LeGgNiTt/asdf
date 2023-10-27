from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Model for schooltypes table
class SchoolType(db.Model):
    __tablename__ = 'schooltypes'
    schooltype_id = db.Column(db.Integer, primary_key=True)
    schooltype_name = db.Column(db.String(255), nullable=False)
    subjects = db.relationship('Subject', backref='schooltype', lazy=True)

# Model for student table
class Student(db.Model):
    __tablename__ = 'student'
    StudentID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50), nullable=True)
    LastName = db.Column(db.String(50), nullable=True)
    DateOfBirth = db.Column(db.Date, nullable=True)

# Model for subjects table
class Subject(db.Model):
    __tablename__ = 'subjects'
    subject_id = db.Column(db.Integer, primary_key=True)
    schooltype_id = db.Column(db.Integer, db.ForeignKey('schooltypes.schooltype_id'), nullable=False)
    subject_name = db.Column(db.String(255), nullable=False)

# Model for tutors table
class Tutor(db.Model):
    __tablename__ = 'tutors'
    tutor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    tutor_subjects = db.relationship('TutorSubject', backref='tutor', lazy=True)

# Model for tutor_subjects table
class TutorSubject(db.Model):
    __tablename__ = 'tutor_subjects'
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutors.tutor_id'), primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'), primary_key=True)

# Model for weekdays table
class Weekday(db.Model):
    __tablename__ = 'weekdays'
    weekday_id = db.Column(db.Integer, primary_key=True)
    weekday_name = db.Column(db.String(50), nullable=False)

# Model for availability table
class Availability(db.Model):
    __tablename__ = 'availability'
    availability_id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutors.tutor_id'), nullable=False)
    weekday_id = db.Column(db.Integer, db.ForeignKey('weekdays.weekday_id'), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

class Lesson(db.Model):
    lesson_id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutors.tutor_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.StudentID'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    tutor = db.relationship('Tutor', backref=db.backref('lessons', lazy=True))
    student = db.relationship('Student', backref=db.backref('lessons', lazy=True))
    subject = db.relationship('Subject', backref=db.backref('lessons', lazy=True))


