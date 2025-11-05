# Django Logger Auth

A Django application for secure authentication event logging with WHOIS lookup and automatic cleanup.

## Features

- 🔐 **Authentication Event Logging**: Automatically logs login, logout, and failed login attempts
- 🌍 **WHOIS Integration**: Automatic geolocation and organization lookup for IP addresses
- ⚙️ **Settings-based Configuration**: No database models needed - configure via Django settings
- 📝 **Flexible Logging**: Support for both file and console logging
- 🧹 **Automatic Cleanup**: Old log entries are automatically deleted based on retention period
- 🔍 **Admin Interface**: Full-featured Django admin with filtering, searching, and bulk actions
- ⏰ **Timezone Aware**: Proper timezone handling and formatting
- 🚀 **Performance Optimized**: Indexed database queries and efficient cleanup

## Installation

Install the package using pip:

```bash
pip install django-logger-auth
```

Or add it to your `requirements.txt`:

```
django-logger-auth>=1.0.0
```

## Quick Start

### 1. Add to INSTALLED_APPS

Add `django_logger_auth` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ... other apps
    'django_logger_auth',
]
```

### 2. Configure Settings

Add the configuration dictionary to your `settings.py`:

```python
DJANGO_LOGGER_AUTH = {
    "enable": True,              # Enable/disable logging (default: True)
    "file_logging": True,        # Log to file (default: True)
    "console_logging": False,    # Log to console/terminal (default: False)
    "whois_lookup": True,        # Enable WHOIS lookup (default: True)
    "keep_days": 30,             # Days to keep logs (default: 30)
}
```

### 3. Run Migrations

Create and apply the database migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Configure Logging (Optional)

If you want file logging, configure a logger in your `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'auth_events_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'auth_events.log',
        },
    },
    'loggers': {
        'auth_events': {
            'handlers': ['auth_events_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

## Usage

Once installed and configured, the app automatically logs authentication events:

- **Login Success**: When a user successfully logs in
- **Logout**: When a user logs out
- **Login Failed**: When a login attempt fails

### Viewing Logs

Access the logs through the Django admin interface at `/admin/`:

1. Navigate to **Authentication Events**
2. Use filters to find specific events
3. Search by username, IP address, or user agent
4. Use bulk actions to delete old records

### Log Format

Log entries are formatted as:

```
[04/Nov/2025 17:51:26] "LOGIN" user=testuser ip=127.0.0.1 whois=Сountry, City; ua="Mozilla/5.0..."
```

### Admin Actions

- **Delete ALL older than Keep days**: Removes all log entries older than the configured retention period

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enable` | bool | `True` | Enable or disable authentication logging |
| `file_logging` | bool | `True` | Enable logging to file |
| `console_logging` | bool | `False` | Enable logging to console/terminal |
| `whois_lookup` | bool | `True` | Enable WHOIS lookup for IP addresses |
| `keep_days` | int | `30` | Number of days to keep log entries |

## Models

### AuthLog

The `AuthLog` model stores authentication events with the following fields:

- `username`: Username (or "unknown" for failed attempts)
- `ip_address`: Client IP address
- `user_agent`: HTTP User-Agent string
- `event_type`: Type of event (login, logout, fail)
- `timestamp`: When the event occurred
- `whois_info`: WHOIS information (country, city, organization)

## Automatic Cleanup

The app automatically deletes old log entries when new events are created. The retention period is controlled by the `keep_days` setting.

## Performance Considerations

- Database indexes are automatically created on `timestamp`, `event_type`, and `ip_address`
- Cleanup is performed in batches to avoid blocking
- WHOIS lookups are synchronous but can be disabled for better performance

## Requirements

- Python 3.10+
- django>=5.0
- requests>=2.32.5
- pytz>2025.2
- ipwhois>=1.3.0



## Troubleshooting

### WHOIS Lookup Failures

If WHOIS lookups are failing, you can disable them:

```python
DJANGO_LOGGER_AUTH = {
    "whois_lookup": False,
    # ... other settings
}
```

### Logs Not Appearing

1. Check that `enable` is set to `True` in settings
2. Verify the app is in `INSTALLED_APPS`
3. Check that migrations have been run
4. Ensure logging is configured if using file logging

### Performance Issues

- Disable WHOIS lookup if not needed
- Reduce `keep_days` to keep fewer records
- Use database indexes (automatically created)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

