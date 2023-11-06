from models import *
from flask import jsonify
import datetime
import calendar


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



def generate_calendar(tutor_id):
    # Get the current date
    today = datetime.date.today()

    # Get the first and last day of the current month
    first_day = today.replace(day=1)
    last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])

    # Retrieve all lessons for the current month for the given tutor_id
    lessons = Lesson.query.filter(
        Lesson.tutor_id == tutor_id,
        Lesson.date.between(first_day, last_day)
    ).all()

    # Organize lessons by date
    calendar_data = {}
    for lesson in lessons:
        lesson_date = lesson.date.strftime('%Y-%m-%d')
        if lesson_date not in calendar_data:
            calendar_data[lesson_date] = []
        calendar_data[lesson_date].append({
            'id': lesson.lesson_id,
            'start_time': lesson.start_time,
            'end_time': lesson.end_time
        })

    # Convert to a list of dates with lessons
    calendar_list = [{'date': key, 'lessons': value} for key, value in calendar_data.items()]

    return jsonify({
        'tutor_id': tutor_id,
        'month': today.month,
        'year': today.year,
        'calendar': calendar_list
    })