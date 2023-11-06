from models import *
from json import jsonify

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