
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from users.models import User
import logging

logger = logging.getLogger(__name__)

@shared_task
def cleanup_deleted_accounts():
    """
    Celery task to permanently delete accounts that requested deletion 30+ days ago
    and have not logged in since.
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=30)
        
        # Find eligible users
        eligible_users = User.objects.filter(
            deletion_requested_at__isnull=False,
            deletion_requested_at__lte=cutoff_date
        ).filter(
            # User either never logged in OR last login was before cutoff
            last_login__isnull=True
        ) | User.objects.filter(
            deletion_requested_at__isnull=False,
            deletion_requested_at__lte=cutoff_date,
            last_login__lte=cutoff_date
        )
        
        eligible_users = eligible_users.distinct()
        count = eligible_users.count()
        
        if count == 0:
            logger.info("No accounts eligible for deletion.")
            return "No accounts eligible for deletion."
            
        logger.info(f"Found {count} account(s) eligible for deletion.")
        
        deleted_count = 0
        for user in eligible_users:
            try:
                username = user.username
                user_id = user.id
                user.delete() 
                deleted_count += 1
                logger.info(f"Deleted user: {username} (ID: {user_id})")
            except Exception as e:
                logger.error(f"Failed to delete user {user.username}: {str(e)}")
                
        return f"Successfully deleted {deleted_count} account(s)."
        
    except Exception as e:
        error_msg = f"Error in cleanup_deleted_accounts task: {str(e)}"
        logger.error(error_msg)
        return error_msg
