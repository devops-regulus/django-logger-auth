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


def get_effective_config() -> EffectiveConfig:
    data = getattr(settings, 'DJANGO_LOGGER_AUTH', {}) or {}
    return EffectiveConfig(data)
