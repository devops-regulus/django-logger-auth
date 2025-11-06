import logging
import threading
import pytz
import requests
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.urls import reverse, NoReverseMatch
from django.utils import timezone
from ipwhois import IPWhois
from .config import get_effective_config
from .models import AuthLog

logger = logging.getLogger("auth_events")


def get_client_ip(request):
    if not request:
        return None
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def get_user_agent(request):
    if not request:
        return "unknown"
    return request.META.get("HTTP_USER_AGENT", "unknown")


def get_local_time():
    try:
        tz = pytz.timezone(settings.TIME_ZONE)
        return timezone.now().astimezone(tz)
    except Exception:
        return timezone.now()


def _whois_lookup_direct(ip, timeout_sec=1.5):
    try:
        obj = IPWhois(ip)
        data = obj.lookup_rdap(depth=1, rate_limit_timeout=timeout_sec)
        country = data.get("network", {}).get("country", "")
        org = data.get("network", {}).get("name", "") or data.get("asn_description", "")
        city = ""
        try:
            r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=timeout_sec)
            if r.status_code == 200:
                info = r.json()
                city = info.get("city", "")
                if not country:
                    country = info.get("country", "")
                if not org:
                    org = info.get("org", "")
        except Exception:
            pass
        return ", ".join(filter(None, [country, city, org])) or "Unknown"
    except Exception as e:
        logger.warning(f"WHOIS lookup failed for {ip}: {e}")
        return "lookup_failed"


def get_audit_config():
    return get_effective_config()


def _log_event_sync(event_type, username, ip, ua):
    """
    Internal function that performs the actual logging synchronously.
    """
    cfg = get_audit_config()
    if not cfg.enabled:
        return

    whois_info = ""
    try:
        if cfg.whois_lookup and ip:
            if str(ip).startswith(("127.", "10.", "192.168", "172.")):
                whois_info = "Local Network"
            else:
                whois_info = _whois_lookup_direct(ip)
    except Exception:
        whois_info = "lookup_failed"

    try:
        AuthLog.objects.create(
            username=username,
            ip_address=ip,
            user_agent=ua,
            event_type=event_type,
            whois_info=whois_info,
        )
    except Exception as e:
        logger.exception(f"Failed to persist AuthLog: {e}")

    local_time = get_local_time().strftime("%d/%b/%Y %H:%M:%S")
    log_line = (
        f"[{local_time}] \"{event_type.upper()}\" "
        f"user={username or 'unknown'} ip={ip or 'unknown'} "
        f"whois={whois_info or '-'} ua=\"{ua or '-'}\""
    )

    if cfg.file_logging:
        if event_type == "fail":
            logger.warning(log_line)
        else:
            logger.info(log_line)

    if cfg.console_logging:
        print(log_line)


def log_event(event_type, username, ip, ua):
    """
    Logs an authentication event asynchronously to avoid blocking the request.
    """
    thread = threading.Thread(
        target=_log_event_sync,
        args=(event_type, username, ip, ua),
        daemon=True
    )
    thread.start()


def is_admin_request(request):
    """
    Determine if the request is for the admin interface based on configuration.
    """
    if not request:
        return False
    from .config import get_effective_config
    cfg = get_effective_config()
    if cfg.log_scope == "all":
        return True
    try:
        admin_login_path = reverse("admin:login")
        base_admin_path = admin_login_path.rsplit("/login", 1)[0]
        return request.path.startswith(base_admin_path)
    except NoReverseMatch:
        return False

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    if is_admin_request(request):
        log_event("login", user.username, get_client_ip(request), get_user_agent(request))


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if is_admin_request(request):
        log_event("logout", user.username, get_client_ip(request), get_user_agent(request))


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    if is_admin_request(request):
        username = credentials.get("username", "unknown")
        log_event("fail", username, get_client_ip(request), get_user_agent(request))
