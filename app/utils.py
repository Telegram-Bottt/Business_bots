import re

PHONE_RE = re.compile(r"^\+?\d{7,15}$")

def valid_phone(phone: str) -> bool:
    return bool(PHONE_RE.match(phone))
