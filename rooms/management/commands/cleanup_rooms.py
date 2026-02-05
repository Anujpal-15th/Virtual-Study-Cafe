"""
Django management command to clean up inactive rooms.
Usage: python manage.py cleanup_rooms
"""
from django.core.management.base import BaseCommand
from rooms.cleanup import run_all_cleanup


class Command(BaseCommand):
    help = 'Clean up inactive and expired rooms older than 30 minutes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting room cleanup...'))
        
        deleted_count = run_all_cleanup()
        
        if deleted_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully cleaned up {deleted_count} room(s)')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('No rooms needed cleanup')
            )
