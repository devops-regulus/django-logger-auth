from django.db import models
from django.utils import timezone
from .config import get_effective_config
from .utils import format_ts, to_local

def get_local_time(ts):
    return to_local(ts)

class AuthLog(models.Model):
    """
    Model to store authentication events.
    """
    EVENT_CHOICES = [
        ("login", "Login success"),
        ("logout", "Logout"),
        ("fail", "Login failed"),
    ]
    username = models.CharField(max_length=150, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    event_type = models.CharField(max_length=10, choices=EVENT_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    extra_info = models.TextField(blank=True, null=True)
    whois_info = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["event_type", "timestamp"]),
            models.Index(fields=["ip_address", "timestamp"]),
        ]
        verbose_name = "Authentication Event"
        verbose_name_plural = "Authentication Events"

    def __str__(self):
        return f"{format_ts(self.timestamp)} {self.username or 'Unknown'} {self.event_type} {self.ip_address or ''}"

    def save(self, *args, **kwargs):
        is_create = self.pk is None
        super().save(*args, **kwargs)
        if is_create:
            try:
                cleanup_old_auth_logs_once(batch_size=1000)
            except Exception:
                pass

class AdminNavigationLog(models.Model):
    """
    Model to store admin panel navigation events.
    """
    auth_log = models.ForeignKey('AuthLog', on_delete=models.CASCADE, related_name='navigation_logs', null=True, blank=True)
    username = models.CharField(max_length=150, db_index=True)
    url_path = models.CharField(max_length=500)
    url_name = models.CharField(max_length=200, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    request_method = models.CharField(max_length=10, default='GET')
    status_code = models.IntegerField(default=200)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["username", "timestamp"]),
            models.Index(fields=["url_path"]),
        ]
        verbose_name = "Admin Navigation Event"
        verbose_name_plural = "Admin Navigation Events"

    def __str__(self):
        return f"{format_ts(self.timestamp)} {self.username} {self.request_method} {self.url_path}"

    def save(self, *args, **kwargs):
        is_create = self.pk is None
        super().save(*args, **kwargs)
        if is_create:
            try:
                cleanup_old_navigation_logs_once(batch_size=1000)
            except Exception:
                pass


def cleanup_old_auth_logs_once(batch_size=1000):
    """
    Delete old auth logs older than keep_days from settings.

    Return the number of deleted records.
    """
    cfg = get_effective_config()
    keep_days = int(getattr(cfg, 'keep_days', 30) or 30)

    cutoff = timezone.now() - timezone.timedelta(days=int(keep_days))
    qs = AuthLog.objects.filter(timestamp__lt=cutoff).order_by('id')
    ids = list(qs.values_list('id', flat=True)[:batch_size])
    if not ids:
        return 0
    deleted, _ = AuthLog.objects.filter(id__in=ids).delete()
    return int(deleted)


def cleanup_old_navigation_logs_once(batch_size=1000):
    """
    Delete old navigation logs older than navigation_keep_days from settings.

    Return the number of deleted records.
    """
    cfg = get_effective_config()
    keep_days = int(getattr(cfg, 'navigation_keep_days', 30) or 30)

    cutoff = timezone.now() - timezone.timedelta(days=int(keep_days))
    qs = AdminNavigationLog.objects.filter(timestamp__lt=cutoff).order_by('id')
    ids = list(qs.values_list('id', flat=True)[:batch_size])
    if not ids:
        return 0
    deleted, _ = AdminNavigationLog.objects.filter(id__in=ids).delete()
    return int(deleted)
