from django.apps import AppConfig

class DjangoLoggerAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_logger_auth'

    def ready(self):
        from . import signals
