from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, time
from flask_bcrypt import Bcrypt, check_password_hash
from flask_login import UserMixin
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

lesson_students = db.Table('lesson_students',
    db.Column('student_id', db.Integer, db.ForeignKey('student.StudentID')),
    db.Column('lesson_id', db.Integer, db.ForeignKey('lesson.lesson_id'))
)

class Paygrade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    role = db.relationship('Role', backref=db.backref('users', lazy=True))
    tutor_profile = db.relationship('Tutor', backref='user', lazy=True)
    paygrade_id = db.Column(db.Integer, db.ForeignKey('paygrade.id'), nullable=False)
    paygrade = db.relationship('Paygrade', backref='users')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_active(self):
        return True

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


class Tutor(db.Model):
    tutor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    availabilities = db.relationship('TutorAvailability', backref='tutor')


class Weekday(db.Model):
    weekday_id = db.Column(db.Integer, primary_key=True)
    weekday_name = db.Column(db.String(50), nullable=False)

class TutorAvailability(db.Model):
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.tutor_id'), primary_key=True)
    weekday_id = db.Column(db.Integer, db.ForeignKey('weekday.weekday_id'), primary_key=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    # Assuming no need to explicitly declare 'tutor' here as it's covered by backref in Tutor
    weekday = db.relationship('Weekday', backref='tutor_availabilities')


class Student(db.Model):
    StudentID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    DateOfBirth = db.Column(db.Date, nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    preferred_time = db.Column(db.String(50))
    schooltype_id = db.Column(db.Integer, db.ForeignKey('schooltype.schooltype_id'), nullable=False)
    schooltype = db.relationship('SchoolType', backref='student', lazy=True)
    enrolled_lessons = db.relationship('Lesson', secondary=lesson_students, lazy='subquery', backref=db.backref('students', lazy='dynamic'))
    phone_num = db.Column(db.String(20), nullable=True)


class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    phone_num = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    entrance_fee = db.Column(db.Float, default=False)

class PriceAdjustment(db.Model):
    __tablename__ = 'price_adjustment'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    value = db.Column(db.Float, nullable=False)

    lessons = db.relationship('Lesson', backref='price_adjustment', lazy='dynamic')

class LessonType(db.Model):
    __tablename__ = 'lesson_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    value = db.Column(db.Float, nullable=False)

    lessons = db.relationship('Lesson', backref='lesson_type', lazy='dynamic')

class Lesson(db.Model):
    lesson_id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.tutor_id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    notes = db.relationship('Note', backref='lesson', lazy=True)
    has_occured = db.Column(db.Boolean, default=False)
    price = db.Column(db.Float)
    price_adjustment_id = db.Column(db.Integer, db.ForeignKey('price_adjustment.id'), nullable=True)
    final_price = db.Column(db.Float)
    lesson_type_id = db.Column(db.Integer, db.ForeignKey('lesson_type.id'), nullable=True)




class SchoolType(db.Model):
    __tablename__ = 'schooltype'
    schooltype_id = db.Column(db.Integer, primary_key=True)
    schooltype_name = db.Column(db.String(255), nullable=False)
    subject = db.relationship('Subject', backref='schooltype', lazy=True)

class Subject(db.Model):
    __tablename__ = 'subject'
    subject_id = db.Column(db.Integer, primary_key=True)
    schooltype_id = db.Column(db.Integer, db.ForeignKey('schooltype.schooltype_id'), nullable=False)
    subject_name = db.Column(db.String(255), nullable=False)

class TutorSubject(db.Model):
    __tablename__ = 'tutorsubject'
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.tutor_id'), primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id'), primary_key=True)

    tutor = db.relationship('Tutor', backref='tutor_subjects', lazy=True)
    subject = db.relationship('Subject', backref='tutor_subjects', lazy=True)

class Note(db.Model):
    __tablename__ = 'note'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.StudentID'))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.lesson_id'))
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.tutor_id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'lesson_id': self.lesson_id,
            'tutor_id': self.tutor_id,
            'subject_id': self.subject_id,
            'date': self.date,
            'content': self.content
        }
