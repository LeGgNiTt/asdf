from app import send_whatsapp_message, db
from datetime import datetime, timedelta
from models import Lesson, Tutor, Contacted, Family
import phonenumbers

def format_number(phone_number):
    try:
        parsed_number = phonenumbers.parse(phone_number, "CH")  # 'CH' is the country code for Switzerland
        formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        return formatted_number
    except phonenumbers.NumberParseException:
        return None  # or handle the error as you prefer



def run_send_whatsapp_reminders():
    now = datetime.now()
    upcomming_lessons = Lesson.query.filter(Lesson.date.between(now, now + timedelta(hours=24))).all()
    for lesson in upcomming_lessons:
        tutor = Tutor.query.filter_by(tutor_id=lesson.tutor_id).first()
        tutor_phone_num = tutor.phone_num
        tutor_phone_num = format_number(tutor_phone_num)
        text = "reminder of upcomming lecture at " + str(lesson.date) + " from: " + str(lesson.start_time) + " to: " + str(lesson.end_time) 
        if tutor_phone_num and not Contacted.query.filter_by(lesson_id=lesson.lesson_id, phone_num=tutor_phone_num).first():
            send_whatsapp_message(tutor_phone_num, text)
            db.session.add(Contacted(lesson_id=lesson.id, phone_num=tutor_phone_num))
        students = lesson.students
        for student in students:
            student_phone_num = student.phone_num
            student_phone_num = format_number(student_phone_num)
            if student_phone_num and not Contacted.query.filter_by(lesson_id=lesson.lesson_id, phone_num=student_phone_num).first():
                send_whatsapp_message(student_phone_num, text)
                db.session.add(Contacted(lesson_id=lesson.id, phone_num=student_phone_num))
            family = Family.query.filter_by(family_id=student.family_id).first()
            family_phone_num = family.phone_num
            family_phone_num = format_number(family_phone_num)
            if family_phone_num != student_phone_num and not Contacted.query.filter_by(lesson_id=lesson.lesson_id, phone_num=family_phone_num).first():
                send_whatsapp_message(family_phone_num, text)
                db.session.add(Contacted(lesson_id=lesson.id, phone_num=family_phone_num))
    db.session.commit()

if __name__ == "__main__":
    run_send_whatsapp_reminders()