"""
Background scheduler for automatic room cleanup.
Runs cleanup every 5 minutes to remove inactive rooms.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

logger = logging.getLogger(__name__)

scheduler = None


def start_scheduler():
    """
    Start the background scheduler for room cleanup.
    Only starts in production or if DEBUG is True.
    Prevents multiple schedulers from starting.
    """
    global scheduler
    
    # Prevent multiple schedulers
    if scheduler is not None:
        logger.info("Scheduler already running, skipping initialization")
        return
    
    # Only run scheduler if not already running
    try:
        from rooms.cleanup import run_all_cleanup
        
        scheduler = BackgroundScheduler()
        
        # Add cleanup job - runs every 5 minutes
        scheduler.add_job(
            run_all_cleanup,
            trigger=IntervalTrigger(minutes=5),
            id='room_cleanup_job',
            name='Clean up inactive rooms',
            replace_existing=True,
            max_instances=1  # Prevent overlapping executions
        )
        
        scheduler.start()
        logger.info("Room cleanup scheduler started (runs every 5 minutes)")
        
    except Exception as e:
        logger.error(f"Failed to start room cleanup scheduler: {str(e)}")


def stop_scheduler():
    """
    Stop the background scheduler.
    """
    global scheduler
    
    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        logger.info("Room cleanup scheduler stopped")
