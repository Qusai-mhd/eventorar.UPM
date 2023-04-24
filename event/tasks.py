from django.core.mail import EmailMessage
from celery import shared_task
from .models import  PublishedEvent
from authentication.models import CustomUser

# @shared_task
def send_qr_code(user_id, event_id, qr_code_buffer):
    user = CustomUser.objects.get(id=user_id)
    event = PublishedEvent.objects.get(id=event_id)

    subject = f"QR code for event {event.event.name}"
    message = 'Please find your QR code attached.'
    from_email = 'eventorar@gmail.com'
    to = [user.email]
    #to = ['ad.min11@hotmail.com']

    email = EmailMessage(subject, message, from_email, to)
    email.attach('qr_code.png', qr_code_buffer.getvalue(), 'image/png')
    email.send()
