import string
from datetime import datetime
import random


def create_ref_code():
    now = datetime.now()
    code = now.strftime("%y%m%d%H%M%S")
    unique_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    ref_code = f"{code}-{unique_id}"
    return ref_code
