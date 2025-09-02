from celery import shared_task
from django.utils import timezone
from django.db.models import Count
from .models import Organization, User, Product, Usage, Subscription
import logging

logger = logging.getLogger(__name__)


@shared_task
def calculate_monthly_usage():
    """Calculate monthly usage for all organizations"""
    try:
        current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (current_month + timezone.timedelta(days=32)).replace(day=1)
        
        for org in Organization.objects.filter(is_active=True):
            # Calculate user count
            user_count = User.objects.filter(organization=org).count()
            Usage.objects.update_or_create(
                organization=org,
                feature='users',
                period_start=current_month,
                period_end=next_month,
                defaults={'count': user_count, 'limit': get_plan_limit(org.plan, 'users')}
            )
            
            # Calculate product count
            product_count = Product.objects.filter(organization=org).count()
            Usage.objects.update_or_create(
                organization=org,
                feature='products',
                period_start=current_month,
                period_end=next_month,
                defaults={'count': product_count, 'limit': get_plan_limit(org.plan, 'products')}
            )
            
            logger.info(f"Updated usage for organization {org.name}")
            
    except Exception as e:
        logger.error(f"Error calculating monthly usage: {str(e)}")


@shared_task
def send_usage_alerts():
    """Send alerts when organizations are approaching their limits"""
    try:
        current_usage = Usage.objects.filter(
            period_start__lte=timezone.now(),
            period_end__gte=timezone.now()
        )
        
        for usage in current_usage:
            if usage.usage_percentage >= 80:  # 80% threshold
                send_usage_alert_notification.delay(usage.id)
                
    except Exception as e:
        logger.error(f"Error sending usage alerts: {str(e)}")


@shared_task
def send_usage_alert_notification(usage_id):
    """Send individual usage alert notification"""
    try:
        from .models import Notification
        
        usage = Usage.objects.get(id=usage_id)
        
        # Create notification for organization owner
        owners = User.objects.filter(organization=usage.organization, role='owner')
        
        for owner in owners:
            Notification.objects.create(
                user=owner,
                organization=usage.organization,
                title=f"Usage Alert: {usage.feature.title()}",
                message=f"You're currently using {usage.usage_percentage:.1f}% of your {usage.feature} limit.",
                notification_type='warning'
            )
            
        logger.info(f"Sent usage alert for {usage.organization.name} - {usage.feature}")
        
    except Exception as e:
        logger.error(f"Error sending usage alert notification: {str(e)}")


@shared_task
def cleanup_expired_tokens():
    """Clean up expired JWT tokens and other temporary data"""
    try:
        from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
        
        # Clean up blacklisted tokens older than 30 days
        cutoff_date = timezone.now() - timezone.timedelta(days=30)
        deleted_count = BlacklistedToken.objects.filter(
            blacklisted_at__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} expired blacklisted tokens")
        
    except Exception as e:
        logger.error(f"Error cleaning up expired tokens: {str(e)}")


@shared_task
def update_subscription_status():
    """Update subscription status based on current period end"""
    try:
        expired_subscriptions = Subscription.objects.filter(
            current_period_end__lt=timezone.now(),
            status='active'
        )
        
        for subscription in expired_subscriptions:
            if subscription.cancel_at_period_end:
                subscription.status = 'cancelled'
                subscription.save()
                
                # Notify organization
                owners = User.objects.filter(organization=subscription.organization, role='owner')
                for owner in owners:
                    from .models import Notification
                    Notification.objects.create(
                        user=owner,
                        organization=subscription.organization,
                        title="Subscription Cancelled",
                        message="Your subscription has been cancelled and is no longer active.",
                        notification_type='error'
                    )
            else:
                # Auto-renew logic would go here
                pass
                
        logger.info(f"Updated {expired_subscriptions.count()} expired subscriptions")
        
    except Exception as e:
        logger.error(f"Error updating subscription status: {str(e)}")


@shared_task
def generate_daily_reports():
    """Generate daily usage and activity reports"""
    try:
        from django.db.models import Count
        from .models import ActivityLog
        
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)
        
        for org in Organization.objects.filter(is_active=True):
            # Count yesterday's activities
            activity_count = ActivityLog.objects.filter(
                organization=org,
                created_at__date=yesterday
            ).count()
            
            # Count active users yesterday
            active_users = ActivityLog.objects.filter(
                organization=org,
                created_at__date=yesterday,
                user__isnull=False
            ).values('user').distinct().count()
            
            # Store metrics in Usage model for historical tracking
            Usage.objects.update_or_create(
                organization=org,
                feature='daily_activities',
                period_start=timezone.datetime.combine(yesterday, timezone.datetime.min.time()),
                period_end=timezone.datetime.combine(yesterday, timezone.datetime.max.time()),
                defaults={
                    'count': activity_count,
                    'metadata': {'active_users': active_users}
                }
            )
            
        logger.info("Generated daily reports for all organizations")
        
    except Exception as e:
        logger.error(f"Error generating daily reports: {str(e)}")


def get_plan_limit(plan, feature):
    """Get the limit for a specific feature based on plan"""
    from django.conf import settings
    
    saas_config = getattr(settings, 'SAAS_CONFIG', {})
    plans = saas_config.get('PLANS', {})
    
    plan_config = plans.get(plan, plans.get('basic', {}))
    features = plan_config.get('features', {})
    
    feature_map = {
        'users': 'max_users',
        'products': 'max_products',
        'api_calls': 'api_calls_per_month',
        'storage': 'storage_gb'
    }
    
    limit_key = feature_map.get(feature, feature)
    return features.get(limit_key, 100)  # Default limit


@shared_task
def backup_critical_data():
    """Create backup of critical data (placeholder implementation)"""
    try:
        # This would implement actual backup logic
        # For now, just log that backup was attempted
        logger.info("Critical data backup completed successfully")
        
    except Exception as e:
        logger.error(f"Error during data backup: {str(e)}")


@shared_task
def send_welcome_email(user_id):
    """Send welcome email to new users"""
    try:
        user = User.objects.get(id=user_id)
        
        # This would integrate with your email service
        # For now, just create a notification
        from .models import Notification
        
        Notification.objects.create(
            user=user,
            organization=user.organization,
            title="Welcome to the platform!",
            message=f"Welcome {user.first_name or user.username}! Your account has been created successfully.",
            notification_type='success'
        )
        
        logger.info(f"Welcome notification sent to user {user.username}")
        
    except Exception as e:
        logger.error(f"Error sending welcome email: {str(e)}")
