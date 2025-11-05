from django.conf import settings
from django.contrib import admin
from .models import AuthLog
from .utils import format_ts, to_local

def get_local_time(ts):
    return to_local(ts)

@admin.register(AuthLog)
class AuthLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp_local", "username", "event_type", "ip_address", "whois_info")
    list_filter = ("event_type", "timestamp", "ip_address")
    search_fields = ("username", "ip_address", "user_agent", "whois_info")
    readonly_fields = ("username", "ip_address", "event_type", "user_agent", "whois_info")
    ordering = ()
    date_hierarchy = "timestamp"
    fields = (
        "username",
        "event_type",
        "ip_address",
        "user_agent",
        "whois_info",
    )

    def timestamp_local(self, obj):
        return format_ts(obj.timestamp)

    timestamp_local.short_description = f"Timestamp ({settings.TIME_ZONE})"
    timestamp_local.admin_order_field = "timestamp"

    def has_add_permission(self, request):
        return False

    def timestamp_local_display(self, obj):
        return format_ts(obj.timestamp)

    timestamp_local_display.short_description = f"Timestamp ({settings.TIME_ZONE})"
