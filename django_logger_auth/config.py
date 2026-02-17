from django.conf import settings

class EffectiveConfig:
    """
    Class to store the effective configuration for the Django Secure Logs app.
    """
    def __init__(self, data):
        self.enabled = bool(data.get('enable', True))
        self.file_logging = bool(data.get('file_logging', True))
        self.console_logging = bool(data.get('console_logging', False))
        self.whois_lookup = bool(data.get('whois_lookup', True))
        self.keep_days = int(data.get('keep_days', 30))
        self.log_scope = data.get('log_scope', 'admin').lower()
        if self.log_scope not in ('all', 'admin'):
            self.log_scope = 'admin'
        self.enable_navigation_logging = bool(data.get('enable_navigation_logging', True))
        self.navigation_keep_days = int(data.get('navigation_keep_days', 30))
        
        # Auto-detect admin URL from Django settings or use manual override
        if 'admin_url_prefix' in data:
            # User explicitly set the admin URL
            self.admin_url_prefix = data['admin_url_prefix']
        else:
            # Try to auto-detect from Django settings
            # Check common settings: ADMIN_URL, ADMIN_PREFIX, or fallback to /admin/
            self.admin_url_prefix = getattr(settings, 'ADMIN_URL', None) or \
                                   getattr(settings, 'ADMIN_PREFIX', None) or \
                                   '/admin/'
        
        # Normalize the prefix (ensure leading and trailing slashes)
        if not self.admin_url_prefix.startswith('/'):
            self.admin_url_prefix = '/' + self.admin_url_prefix
        if not self.admin_url_prefix.endswith('/'):
            self.admin_url_prefix = self.admin_url_prefix + '/'
        
        # Excluded paths (paths that should not be logged)
        self.excluded_paths = data.get('excluded_paths', [])
        if not isinstance(self.excluded_paths, list):
            self.excluded_paths = []
        
        # Allow delete in admin panel (default: False for security)
        self.allow_delete = bool(data.get('allow_delete', False))


def get_effective_config() -> EffectiveConfig:
    data = getattr(settings, 'DJANGO_LOGGER_AUTH', {}) or {}
    return EffectiveConfig(data)
