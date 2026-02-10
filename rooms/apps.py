from django.apps import AppConfig


class RoomsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rooms'
    
    def ready(self):
        """
        Import signals when app is ready and start background cleanup scheduler
        """
        import rooms.signals
        
        # Only start scheduler under runserver/daphne, not during migrations/shell
        import sys
        if 'runserver' in sys.argv or 'daphne' in sys.argv[0] if sys.argv else False:
            from rooms.scheduler import start_scheduler
            start_scheduler()
