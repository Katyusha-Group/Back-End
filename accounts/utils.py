import threading

from accounts.models import User


class EmailThread(threading.Thread):
    def __init__(self, email_handler ,subject,recipient_list, verification_token, registration_tries, show_text):
        super().__init__()
        self.email_handler = email_handler
        self.subject = subject
        self.recipient_list = recipient_list
        self.verification_token = verification_token
        self.registration_tries = registration_tries
        self.show_text = show_text

    def run(self):
        self.email_handler.send_verification_message(
            subject=self.subject,
            recipient_list=self.recipient_list,
            verification_token=self.verification_token,
            registration_tries=self.registration_tries,
            show_text=self.show_text
        )
        print(f"Email sent to {self.recipient_list}")

from rest_framework_simplejwt.tokens import RefreshToken


def generate_tokens(user_id):
    refresh = RefreshToken.for_user(User.objects.get(id=user_id))
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
