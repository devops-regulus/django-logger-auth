# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-04

### Added
- Initial release of django-logger-auth
- Authentication event logging for login, logout, and failed login attempts
- Automatic WHOIS lookup for IP addresses with country, city, and organization information
- Configurable logging via Django settings (no database model needed)
- File and console logging support
- Automatic cleanup of old log entries based on configurable retention period
- Django admin interface with filtering, searching, and bulk deletion
- Timezone-aware timestamp formatting
- IP address extraction from X-Forwarded-For headers
- User agent logging
- Comprehensive admin actions for log management

### Features
- **Settings-based configuration**: Configure via `DJANGO_LOGGER_AUTH` in settings.py
- **Automatic cleanup**: Old logs are automatically deleted when new events are created
- **WHOIS integration**: Automatic geolocation and organization lookup for IP addresses
- **Admin interface**: Full-featured Django admin with filtering and search
- **Performance optimized**: Indexed database queries and efficient cleanup

### Configuration
```python
DJANGO_LOGGER_AUTH = {
    "enable": True,
    "file_logging": True,
    "console_logging": False,
    "whois_lookup": True,
    "keep_days": 30,
}
```

### Dependencies
- Django >= 5.0
- ipwhois >= 1.3.0
- requests >= 2.32.5
- pytz >= 2025.2

