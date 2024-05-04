from django.apps import AppConfig


class IndexNowConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'indexnow'

    def ready(self):
        from . import signals
