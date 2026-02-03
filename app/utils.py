import re

PHONE_RE = re.compile(r"^\+?\d{7,15}$")

def valid_phone(phone: str) -> bool:
    return bool(PHONE_RE.match(phone))


def format_rating(avg: float, cnt: int) -> str:
    """Return a formatted rating string or empty string when no reviews.

    Examples:
        format_rating(4.72, 23) -> '⭐ 4.7 (23)'
        format_rating(0.0, 0) -> ''
    """
    try:
        if not cnt or cnt <= 0:
            return ''
        return f"⭐ {avg:.1f} ({cnt})"
    except Exception:
        return ''

def get_args_from_message(message) -> str:
    """Compatibility helper: extract command arguments from a Message.

    aiogram v3 Message object may not have `get_args()` helper used in v2.
    This function returns the text after the first space (or empty string).
    """
    # If the message object provides a get_args() (test fakes or older aiogram), prefer it
    try:
        ga = getattr(message, 'get_args', None)
        if callable(ga):
            try:
                return (ga() or '').strip()
            except TypeError:
                # some fakes might expect no args; fallthrough
                pass
    except Exception:
        pass
    try:
        text = getattr(message, 'text', '') or ''
        parts = text.split(None, 1)
        if len(parts) > 1:
            return parts[1].strip()
        return ''
    except Exception:
        return ''
