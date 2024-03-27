from datetime import datetime, timedelta
import phonenumbers
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
# Add other necessary imports (e.g., SQLAlchemy, your database models)
from app import app, db, format_number, is_valid_number
from models import Tutor, Lesson, Student, Family, Contacted


# Twilio credentials
TWILIO_ACCOUNT_SID = ''
TWILIO_AUTH_TOKEN = ''
TWILIO_WHATSAPP_NUMBER = '+'

TEMPLATES = {
    'reminder_tutor': 'Automatische Erinnerung an die bevorstehende Lektion am {} um {} mit {}.',
    'reminder_student': 'Automatische Erinnerung an die bevorstehende Lektion am {} um {} mit {}.',
    'family_reminder': 'Automatische Erinnerung an die bevorstehende Lektion am {} um {} mit {} für {}.',
}



def send_whatsapp_message(number, text):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    try:
        message = client.messages.create(
            body=text,
            from_=f'whatsapp:{TWILIO_WHATSAPP_NUMBER}',
            to=f'whatsapp:{number}'
        )
        print(f"Message status: {message.status}")  
        print(f"Message sent to {number}: {text}")
    except TwilioException as e:
        print(f"Failed to send message to {number}: {e}")


def send_whatsapp_template_message(number, template_name, parameters):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    try:
        # Format the message according to the template
        template = TEMPLATES[template_name]
        message_body = template.format(*parameters)
        
        message = client.messages.create(
            body=message_body,
            from_=f'whatsapp:{TWILIO_WHATSAPP_NUMBER}',
            to=f'whatsapp:{number}'
        )
        print(f"Message status: {message.status}")
        print(f"Template message sent to {number}: {message_body}")
    except TwilioException as e:
        print(f"Failed to send template message to {number}: {e}")




def send_whatsapp_reminders():
    now = datetime.now()
    upcomming_lessons = Lesson.query.filter(Lesson.date.between(now, now + timedelta(hours=24))).all()
    for lesson in upcomming_lessons:
        lesson_date = str(lesson.date)
        start_time = str(lesson.start_time)
        end_time = str(lesson.end_time)

        tutor = Tutor.query.filter_by(tutor_id=lesson.tutor_id).first()
        tutor_phone_num = tutor.phone_num
        tutor_phone_num = format_number(tutor_phone_num)

        students = lesson.students
        student_names = [f"{student.FirstName} {student.LastName}" for student in students]  # Get the students' names

        if tutor_phone_num is not None:
            if tutor_phone_num and not Contacted.query.filter_by(lesson_id=lesson.lesson_id, phone_num=tutor_phone_num).first():
                tutor_params = [lesson_date, start_time, ', '.join(student_names)]
                send_whatsapp_template_message(tutor_phone_num, 'reminder_tutor', tutor_params)
                db.session.add(Contacted(lesson_id=lesson.lesson_id, phone_num=tutor_phone_num))
            else:
                print(f"Reminder to tutor {tutor.name} not sent: already contacted or invalid number")
        else:
            print(f"Reminder to tutor {tutor.name} not sent: no phone number")
        
        
        
        for student in students:
            student_phone_num = student.phone_num
            student_phone_num = format_number(student_phone_num)
            if student_phone_num is not None:
                if student_phone_num and not Contacted.query.filter_by(lesson_id=lesson.lesson_id, phone_num=student_phone_num).first():
                    student_params = [lesson_date, start_time, tutor.name]
                    send_whatsapp_template_message(student_phone_num, 'reminder_student', student_params)
                    db.session.add(Contacted(lesson_id=lesson.lesson_id, phone_num=student_phone_num))

            student_name = f"{student.FirstName}"
            family = Family.query.filter_by(id=student.family_id).first()
            family_phone_num = family.phone_num
            family_phone_num = format_number(family_phone_num)
            if family_phone_num is not None:
                if family_phone_num != student_phone_num and not Contacted.query.filter_by(lesson_id=lesson.lesson_id, phone_num=family_phone_num).first():
                    family_params = [lesson_date, start_time, student_name, tutor.name]
                    send_whatsapp_template_message(family_phone_num, 'family_reminder', family_params)
                    db.session.add(Contacted(lesson_id=lesson.lesson_id, phone_num=family_phone_num))
    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        send_whatsapp_reminders()