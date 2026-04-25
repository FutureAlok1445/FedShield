from django.apps import AppConfig


class PoisoningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'poisoning'
