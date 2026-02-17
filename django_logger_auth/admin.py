from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from .models import AuthLog, AdminNavigationLog
from .utils import format_ts, to_local
from .config import get_effective_config

def get_local_time(ts):
    return to_local(ts)


class AdminNavigationLogInline(admin.TabularInline):
    """Inline to show navigation logs linked to this authentication session."""
    model = AdminNavigationLog
    extra = 0
    can_delete = False
    max_num = 50  # Show up to 50 records
    fields = ("timestamp_local", "url_path_link", "url_name", "request_method", "status_code_colored")
    readonly_fields = ("timestamp_local", "url_path_link", "url_name", "request_method", "status_code_colored")
    ordering = ("-timestamp",)
    
    def timestamp_local(self, obj):
        return format_ts(obj.timestamp)
    timestamp_local.short_description = f"Час ({settings.TIME_ZONE})"
    
    def url_path_link(self, obj):
        """Display URL path as clickable link."""
        if obj.url_path:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.url_path, obj.url_path)
        return "-"
    url_path_link.short_description = "URL шлях"
    
    def status_code_colored(self, obj):
        """Display status code with color."""
        if obj.status_code < 300:
            color = 'green'
        elif obj.status_code < 400:
            color = 'orange'
        else:
            color = 'red'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.status_code)
    status_code_colored.short_description = "Статус"
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(AuthLog)
class AuthLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp_local", "username", "event_type", "ip_address", "whois_info")
    list_filter = ("event_type", "timestamp", "ip_address")
    search_fields = ("username", "ip_address", "user_agent", "whois_info")
    readonly_fields = ("username", "ip_address", "event_type", "user_agent", "whois_info", "navigation_logs_link")
    ordering = ()
    date_hierarchy = "timestamp"
    fields = (
        "username",
        "event_type",
        "ip_address",
        "user_agent",
        "whois_info",
        "navigation_logs_link",
    )

    def navigation_logs_link(self, obj):
        """Link to navigation logs filtered by this user, date and IP."""
        if not obj or not obj.username:
            return "-"
        
        from django.urls import reverse
        from urllib.parse import urlencode

        date_str = obj.timestamp.strftime('%Y-%m-%d')

        base_url = reverse('admin:django_logger_auth_adminnavigationlog_changelist')
        params = {
            'username': obj.username,
            'timestamp__date': date_str,
        }
        if obj.ip_address:
            params['ip_address'] = obj.ip_address
        
        url = f"{base_url}?{urlencode(params)}"
        
        # Count navigation logs for this session
        count = obj.navigation_logs.count()
        
        return format_html(
            '<a href="{}" target="_blank">Переглянути всі {} записів навігації (фільтр: дата + IP) →</a>',
            url,
            count
        )
    navigation_logs_link.short_description = "Повна навігаційна історія"


    def timestamp_local(self, obj):
        return format_ts(obj.timestamp)

    timestamp_local.short_description = f"Timestamp ({settings.TIME_ZONE})"
    timestamp_local.admin_order_field = "timestamp"

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        cfg = get_effective_config()
        return cfg.allow_delete

class AdminNavigationLogAdmin(admin.ModelAdmin):
    """Admin for navigation logs - accessible only through link from AuthLog."""
    list_display = ("timestamp_local", "username", "url_path_short", "url_name", "request_method", "status_code", "ip_address")
    list_filter = ("timestamp", "username", "request_method", "status_code", "ip_address")
    search_fields = ("username", "url_path", "url_name", "ip_address")
    readonly_fields = ("username", "url_path", "url_name", "ip_address", "user_agent", "timestamp", "request_method", "status_code", "auth_log")
    ordering = ()
    date_hierarchy = "timestamp"
    fields = (
        "username",
        "url_path",
        "url_name",
        "request_method",
        "status_code",
        "ip_address",
        "user_agent",
        "auth_log",
    )

    def timestamp_local(self, obj):
        return format_ts(obj.timestamp)

    timestamp_local.short_description = f"Timestamp ({settings.TIME_ZONE})"
    timestamp_local.admin_order_field = "timestamp"
    
    def url_path_short(self, obj):
        """Truncate long URLs for list display."""
        if len(obj.url_path) > 60:
            return obj.url_path[:57] + "..."
        return obj.url_path
    url_path_short.short_description = "URL Path"

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        cfg = get_effective_config()
        return cfg.allow_delete
    
    def has_module_permission(self, request):
        """Hide from admin index, but keep accessible via direct URL."""
        return False


admin.site.register(AdminNavigationLog, AdminNavigationLogAdmin)

