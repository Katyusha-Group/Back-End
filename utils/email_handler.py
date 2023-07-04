from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from core.settings import EMAIL_HOST
from utils import project_variables


def send_verification_message(subject, recipient_list, verification_token, registration_tries):
    context = {
        'email_verification_token': verification_token,
        'registration_tries': registration_tries,
        'remaining_registration_tries': project_variables.MAX_REGISTRATION_TRIES - registration_tries,
        'image_bg': 'http://katyushaiust.ir/static/Back-End/welcome_bg.png',
        'image_url1': 'http://katyushaiust.ir/static/Back-End/katyusha-activation-image.png'
    }
    html_message = render_to_string('activation_template.html', context)
    email = EmailMultiAlternatives(subject, '', EMAIL_HOST, recipient_list)
    email.attach_alternative(html_message, "text/html")
    email.send()


def send_forget_password_verification_message(subject, recipient_list, verification_token):
    context = {
        'email_verification_token': verification_token,
        'image_bg': 'http://katyushaiust.ir/static/Back-End/ResetPassword_BG_2.png',
        'image_icon': 'http://katyushaiust.ir/static/Back-End/kat_1.png',
        'image_header': 'http://katyushaiust.ir/static/Back-End/Reset_password-bro.png',
    }
    html_message = render_to_string('forget_password.html', context)
    email = EmailMultiAlternatives(subject, '', EMAIL_HOST, recipient_list)
    email.attach_alternative(html_message, "text/html")
    email.send()
