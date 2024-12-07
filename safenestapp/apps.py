from django.apps import AppConfig


class SafenestappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "safenestapp"

    def ready(self):
        import safenestapp.signals