import threading
from django.conf import settings
from django.urls import resolve, Resolver404
from .config import get_effective_config
from .models import AdminNavigationLog


def get_client_ip(request):
    """Extract client IP from request."""
    if not request:
        return None
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def get_user_agent(request):
    """Extract user agent from request."""
    if not request:
        return "unknown"
    return request.META.get("HTTP_USER_AGENT", "unknown")


def is_admin_request(request, cfg):
    """Check if request is for admin path based on configuration."""
    if not request:
        return False
    return request.path.startswith(cfg.admin_url_prefix)


def is_excluded_path(request, cfg):
    """Check if request path should be excluded from logging."""
    if not request or not cfg.excluded_paths:
        return False
    
    for excluded_path in cfg.excluded_paths:
        if request.path == excluded_path or request.path.startswith(excluded_path):
            return True
    
    return False





def resolve_url_name(path):
    """Try to resolve URL name from path."""
    try:
        resolved = resolve(path)
        if resolved.url_name:
            if resolved.namespace:
                return f"{resolved.namespace}:{resolved.url_name}"
            return resolved.url_name
    except Resolver404:
        pass
    return None


def _log_navigation_sync(username, url_path, url_name, ip, ua, method, status, auth_log=None):
    """Internal function to log navigation synchronously."""
    try:
        AdminNavigationLog.objects.create(
            username=username,
            url_path=url_path,
            url_name=url_name or '',
            ip_address=ip,
            user_agent=ua,
            request_method=method,
            status_code=status,
            auth_log=auth_log,
        )
    except Exception as e:
        import logging
        logger = logging.getLogger('django_logger_auth')
        logger.error(f"Failed to log navigation: {e}", exc_info=True)


def log_navigation(username, url_path, url_name, ip, ua, method, status, auth_log=None):
    """Log navigation asynchronously."""
    thread = threading.Thread(
        target=_log_navigation_sync,
        args=(username, url_path, url_name, ip, ua, method, status, auth_log),
        daemon=True
    )
    thread.start()


class AdminNavigationLoggingMiddleware:
    """
    Middleware to log admin panel navigation.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        cfg = get_effective_config()

        if not cfg.enable_navigation_logging:
            return self.get_response(request)

        if not is_admin_request(request, cfg):
            return self.get_response(request)

        if not request.user or not request.user.is_authenticated:
            return self.get_response(request)

        # Check if path is excluded from logging
        if is_excluded_path(request, cfg):
            return self.get_response(request)

        username = request.user.username
        url_path = request.path
        url_name = resolve_url_name(url_path)
        ip = get_client_ip(request)
        ua = get_user_agent(request)
        method = request.method

        from .models import AuthLog
        from django.utils import timezone
        from datetime import timedelta
        
        auth_log = None
        try:
            cutoff = timezone.now() - timedelta(hours=24)
            auth_log = AuthLog.objects.filter(
                username=username,
                event_type='login',
                timestamp__gte=cutoff
            ).order_by('-timestamp').first()
        except Exception:
            pass

        response = self.get_response(request)

        log_navigation(
            username=username,
            url_path=url_path,
            url_name=url_name,
            ip=ip,
            ua=ua,
            method=method,
            status=response.status_code,
            auth_log=auth_log
        )
        
        return response
