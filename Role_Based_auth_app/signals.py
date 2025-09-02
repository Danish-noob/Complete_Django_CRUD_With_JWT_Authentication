from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Organization, User, Product, ActivityLog, Usage, Subscription
from django.utils import timezone

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile_activity(sender, instance, created, **kwargs):
    """Create activity log when user is created or updated"""
    if created:
        ActivityLog.objects.create(
            organization=instance.organization,
            user=instance,
            action='create',
            resource_type='User',
            resource_id=str(instance.id),
            description=f"User {instance.username} was created"
        )
    else:
        ActivityLog.objects.create(
            organization=instance.organization,
            user=instance,
            action='update',
            resource_type='User', 
            resource_id=str(instance.id),
            description=f"User {instance.username} was updated"
        )


@receiver(post_save, sender=Product)
def create_product_activity(sender, instance, created, **kwargs):
    """Create activity log when product is created or updated"""
    if created:
        ActivityLog.objects.create(
            organization=instance.organization,
            user=instance.created_by,
            action='create',
            resource_type='Product',
            resource_id=str(instance.id),
            description=f"Product {instance.product_name or instance.name} was created"
        )
    else:
        ActivityLog.objects.create(
            organization=instance.organization,
            user=instance.updated_by,
            action='update',
            resource_type='Product',
            resource_id=str(instance.id),
            description=f"Product {instance.product_name or instance.name} was updated"
        )


@receiver(post_delete, sender=Product)
def create_product_delete_activity(sender, instance, **kwargs):
    """Create activity log when product is deleted"""
    ActivityLog.objects.create(
        organization=instance.organization,
        user=None,  # We can't track who deleted it from here
        action='delete',
        resource_type='Product',
        resource_id=str(instance.id),
        description=f"Product {instance.product_name or instance.name} was deleted"
    )


@receiver(post_save, sender=Organization)
def create_organization_subscription(sender, instance, created, **kwargs):
    """Create default subscription when organization is created"""
    if created:
        # Create basic subscription for new organizations
        Subscription.objects.get_or_create(
            organization=instance,
            defaults={
                'plan': 'basic',
                'status': 'active',
                'current_period_start': timezone.now(),
                'current_period_end': timezone.now() + timezone.timedelta(days=30)
            }
        )
        
        # Create initial usage records
        features = ['users', 'products', 'api_calls', 'storage']
        for feature in features:
            Usage.objects.get_or_create(
                organization=instance,
                feature=feature,
                period_start=timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
                period_end=timezone.now().replace(day=1, hour=23, minute=59, second=59, microsecond=999999) + timezone.timedelta(days=31),
                defaults={
                    'count': 0,
                    'limit': 100 if feature == 'products' else 1000
                }
            )


@receiver(post_save, sender=User)
def update_user_count(sender, instance, created, **kwargs):
    """Update organization's user usage count"""
    if created and instance.organization:
        current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (current_month + timezone.timedelta(days=32)).replace(day=1)
        
        usage, created_usage = Usage.objects.get_or_create(
            organization=instance.organization,
            feature='users',
            period_start=current_month,
            period_end=next_month,
            defaults={'count': 0, 'limit': 5}
        )
        
        if not created_usage:
            usage.count += 1
            usage.save()


@receiver(post_save, sender=Product)
def update_product_count(sender, instance, created, **kwargs):
    """Update organization's product usage count"""
    if created and instance.organization:
        current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (current_month + timezone.timedelta(days=32)).replace(day=1)
        
        usage, created_usage = Usage.objects.get_or_create(
            organization=instance.organization,
            feature='products',
            period_start=current_month,
            period_end=next_month,
            defaults={'count': 0, 'limit': 100}
        )
        
        if not created_usage:
            usage.count += 1
            usage.save()


@receiver(pre_save, sender=User)
def update_last_activity(sender, instance, **kwargs):
    """Update user's last activity timestamp"""
    if instance.pk:  # Only for existing users
        try:
            old_instance = User.objects.get(pk=instance.pk)
            if old_instance.last_login != instance.last_login:
                instance.last_activity = timezone.now()
                instance.login_count = (instance.login_count or 0) + 1
        except User.DoesNotExist:
            pass
