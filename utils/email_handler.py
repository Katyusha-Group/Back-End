from django.core.mail import send_mail
from django.template.loader import render_to_string

from core.settings import EMAIL_HOST


def send_verification_message(subject, recipient_list, verification_token):
    context = {
        'email_verification_token': verification_token,
    }
    html_message = render_to_string('activation_template.html', context)
    send_mail(subject, "", EMAIL_HOST, recipient_list, html_message=html_message)
