from django.apps import AppConfig


class RoomsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rooms'
    
    def ready(self):
        """
        Import signals when app is ready and start background cleanup scheduler
        """
        import rooms.signals
        
        # Start the room cleanup scheduler
        from rooms.scheduler import start_scheduler
        start_scheduler()
