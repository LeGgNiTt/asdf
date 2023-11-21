from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, time
from flask_bcrypt import Bcrypt, check_password_hash
from flask_login import UserMixin
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    role = db.relationship('Role', backref=db.backref('users', lazy=True))
    tutor_profile = db.relationship('Tutor', backref='user', lazy=True)

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

class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    phone_num = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class Lesson(db.Model):
    lesson_id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.tutor_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.StudentID'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

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


