from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from core.settings import EMAIL_HOST
from utils import project_variables


def send_verification_message(subject, recipient_list, verification_token, registration_tries, show_text):
    remaining_registration_tries = project_variables.MAX_VERIFICATION_TRIES - registration_tries
    if show_text:
        if remaining_registration_tries < project_variables.MAX_VERIFICATION_TRIES:
            remaining_text = f'تا کنون به تعداد {registration_tries}بار، ' \
                             f'درخواست ثبت نام داشته اید. به تعداد {remaining_registration_tries} ' \
                             f'دفعۀ دیگر میتوانید برای دریافت کد تایید، درخواست نمایید. ' \
                             f'بعد از آن، پس از 12 ساعت انتظار، می توانید ' \
                             f'برای باری دیگر، برای دریافت کد تایید، درخواست خود را در سامانه ثبت کنید.'
        else:
            remaining_text = 'به سقف مجاز برای ثبت درخواست کد تایید رسیده اید. ' \
                             'پس از 12 ساعت انتظار، می توانید برای باری دیگر، برای دریافت کد تایید، درخواست نمایید.'
    else:
        remaining_text = ''
    context = {
        'email_verification_token': verification_token,
        'remaining_text': remaining_text,
        'image_bg': 'http://katyushaiust.ir/static/Back-End/welcome_bg.png',
        'image_url1': 'http://katyushaiust.ir/static/Back-End/katyusha-activation-image.png'
    }
    html_message = render_to_string('activation_template.html', context)
    email = EmailMultiAlternatives(subject, '', EMAIL_HOST, recipient_list)
    email.attach_alternative(html_message, "text/html")
    email.send()


def send_forget_password_verification_message(subject, recipient_list, verification_token, verification_tries):
    remaining_verification_tries = project_variables.MAX_VERIFICATION_TRIES - verification_tries
    if remaining_verification_tries < project_variables.MAX_VERIFICATION_TRIES:
        remaining_text = f'تا کنون به تعداد {verification_tries}بار، ' \
                         f'درخواست تغییر رمز عبور داشته اید. به تعداد {remaining_verification_tries} ' \
                         f'دفعۀ دیگر می توانید برای دریافت کد تایید، درخواست نمایید. ' \
                         f'بعد از آن، پس از 12 ساعت انتظار، می توانید ' \
                         f'برای باری دیگر، برای دریافت کد تایید، درخواست خود را در سامانه ثبت کنید.'
    else:
        remaining_text = 'به سقف مجاز برای ثبت درخواست کد تایید رسیده اید. ' \
                         'پس از 12 ساعت انتظار، می توانید برای باری دیگر، برای دریافت کد تایید، درخواست نمایید.'
    context = {
        'email_verification_token': verification_token,
        'remaining_text': remaining_text,
        'image_bg': 'http://katyushaiust.ir/static/Back-End/ResetPassword_BG_2.png',
        'image_icon': 'http://katyushaiust.ir/static/Back-End/kat_1.png',
        'image_header': 'http://katyushaiust.ir/static/Back-End/Reset_password-bro.png',
    }
    html_message = render_to_string('forget_password.html', context)
    email = EmailMultiAlternatives(subject, '', EMAIL_HOST, recipient_list)
    email.attach_alternative(html_message, "text/html")
    email.send()
