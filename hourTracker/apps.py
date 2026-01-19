from django.apps import AppConfig

class HourtrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hourTracker'

    def ready(self):
        # This imports the signals file when the app starts
        import hourTracker.signals