import pytz
from django.conf import settings
from django.utils import timezone

def to_local(dt):
    try:
        tz = pytz.timezone(settings.TIME_ZONE)
        return dt.astimezone(tz)
    except Exception:
        return dt

def now_local():
    try:
        tz = pytz.timezone(settings.TIME_ZONE)
        return timezone.now().astimezone(tz)
    except Exception:
        return timezone.now()

def format_ts(dt):
    dt_local = to_local(dt)
    return dt_local.strftime("%d/%b/%Y %H:%M:%S")
