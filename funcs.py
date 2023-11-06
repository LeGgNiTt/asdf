from models import *
from flask import jsonify



def find_tutor_by_subject(subject_id):
    tutors = db.session.query(Tutor).join(TutorSubject).filter(TutorSubject.subject_id == subject_id).all()
    return jsonify([{'id': tutor.tutor_id, 'name': tutor.name} for tutor in tutors])


def check_lessons(tutor_id, date):
    lessons = Lesson.query.filter_by(tutor_id=tutor_id, date=date).all()
    return jsonify([{'id': lesson.lesson_id, 'start_time': lesson.start_time, 'end_time': lesson.end_time} for lesson in lessons])

def create_lesson(tutor_id, student_id, subject_id, date, start_time, end_time):
    new_lesson = Lesson(tutor_id=tutor_id, student_id=student_id, subject_id=subject_id, 
                        date=date, start_time=start_time, end_time=end_time)

    # Add to the database
    db.session.add(new_lesson)
    db.session.commit()

    return jsonify({'message': 'Lesson created successfully!'})


import datetime
import calendar

def generate_calendar(tutor_id):
    # Get the current date
    today = datetime.date.today()

    # Get the first day of the current month
    first_day = today.replace(day=1)

    # Get the number of days in the current month
    _, num_days = calendar.monthrange(today.year, today.month)

    # Generate a list of dates for the current month
    dates = [first_day + datetime.timedelta(days=i) for i in range(num_days)]

    # Create a list of lessons for the current month for the given tutor_id
    lessons = []
    for date in dates:
        lessons_for_date = check_lessons(tutor_id, date)
        lessons.append({'date': date, 'lessons': lessons_for_date})

    return jsonify({'tutor_id': tutor_id, 'month': today.month, 'year': today.year, 'lessons': lessons})
