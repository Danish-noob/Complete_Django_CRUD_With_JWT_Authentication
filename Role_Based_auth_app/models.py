from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid
import secrets

class Organization(models.Model):
    """Multi-tenant organization model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=100)
    domain = models.CharField(max_length=255, unique=True, null=True, blank=True)
    logo = models.ImageField(upload_to='org_logos/', null=True, blank=True)
    description = models.TextField(blank=True)
    
    # Subscription info
    plan = models.CharField(max_length=50, default='basic')
    is_active = models.BooleanField(default=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)
    
    # Settings
    settings = models.JSONField(default=dict)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def is_trial_expired(self):
        if self.trial_end_date:
            return timezone.now() > self.trial_end_date
        return False

class User(AbstractUser):
    """Enhanced user model with organization and role support"""
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('user', 'User'),
        ('viewer', 'Viewer'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='users',
        null=True, blank=True
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    
    # Profile fields
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    bio = models.TextField(blank=True)
    
    # Verification and security
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=255, blank=True)
    password_reset_token = models.CharField(max_length=255, blank=True)
    two_factor_enabled = models.BooleanField(default=False)
    
    # Activity tracking
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    login_count = models.PositiveIntegerField(default=0)
    
    # Preferences
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    notifications_enabled = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.role}) - {self.organization}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def has_permission(self, permission):
        """Check if user has specific permission based on role"""
        role_permissions = {
            'owner': ['all'],
            'admin': ['create_user', 'delete_user', 'create_product', 'delete_product', 'view_analytics'],
            'manager': ['create_product', 'edit_product', 'view_products'],
            'user': ['view_products', 'create_order'],
            'viewer': ['view_products'],
        }
        user_permissions = role_permissions.get(self.role, [])
        return permission in user_permissions or 'all' in user_permissions

class Category(models.Model):
    """Product categories with organization isolation"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['organization', 'slug']
        ordering = ['sort_order', 'name']
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"

class Product(models.Model):
    """Enhanced product model with organization isolation"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Basic info - keeping original fields for compatibility
    product_name = models.CharField(max_length=255)  # Original field
    name = models.CharField(max_length=255, blank=True)  # New field
    slug = models.SlugField(max_length=100, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    
    # Pricing and inventory - keeping original fields
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    sku = models.CharField(max_length=100, unique=True, blank=True)
    
    # Status and visibility
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_digital = models.BooleanField(default=False)
    
    # SEO and metadata
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    # Tracking
    view_count = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(5.00)]
    )
    review_count = models.PositiveIntegerField(default=0)
    
    # User tracking
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_products', null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_products', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['organization', 'category']),
            models.Index(fields=['sku']),
        ]
    
    def __str__(self):
        return self.product_name or self.name
    
    def save(self, *args, **kwargs):
        # Auto-populate name from product_name for backward compatibility
        if not self.name and self.product_name:
            self.name = self.product_name
        # Auto-generate SKU if not provided
        if not self.sku:
            self.sku = f"PRD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def effective_price(self):
        return self.sale_price if self.sale_price else self.price
    
    @property
    def is_in_stock(self):
        return self.quantity > 0
    
    @property
    def profit_margin(self):
        if self.cost_price:
            return ((self.effective_price - self.cost_price) / self.effective_price) * 100
        return 0

class ProductImage(models.Model):
    """Product images with multiple image support"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['sort_order', 'created_at']
    
    def save(self, *args, **kwargs):
        if self.is_primary:
            # Ensure only one primary image per product
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)

class Subscription(models.Model):
    """Organization subscription management"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='subscription')
    
    # Plan details
    plan = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default='active')
    
    # Stripe integration
    stripe_customer_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    
    # Billing
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.organization.name} - {self.plan}"
    
    @property
    def is_active(self):
        return self.status == 'active' and timezone.now() < self.current_period_end

class Usage(models.Model):
    """Track organization usage for billing and limits"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='usage_records')
    
    # Usage metrics
    feature = models.CharField(max_length=100)
    count = models.PositiveIntegerField(default=0)
    limit = models.PositiveIntegerField(null=True, blank=True)
    
    # Time period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['organization', 'feature', 'period_start']
        indexes = [
            models.Index(fields=['organization', 'feature']),
            models.Index(fields=['period_start', 'period_end']),
        ]
    
    @property
    def usage_percentage(self):
        if self.limit and self.limit > 0:
            return (self.count / self.limit) * 100
        return 0
    
    @property
    def is_limit_exceeded(self):
        return self.limit and self.limit > 0 and self.count >= self.limit

class FileUpload(models.Model):
    """File upload management with organization isolation"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='files')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    
    # File details
    file = models.FileField(upload_to='uploads/')
    original_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)
    
    # Metadata
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    is_public = models.BooleanField(default=False)
    
    # Security
    access_key = models.CharField(max_length=255, unique=True, null=True, blank=True)
    download_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.original_name} - {self.organization.name}"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            self.original_name = self.original_name or self.file.name
        super().save(*args, **kwargs)
    
    @property
    def file_size_formatted(self):
        """Return human readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

class APIKey(models.Model):
    """API keys for organization access"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='api_keys')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_api_keys')
    
    # Key details
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255, unique=True)
    key_preview = models.CharField(max_length=20)
    
    # Permissions and limits
    permissions = models.JSONField(default=list)
    rate_limit = models.PositiveIntegerField(default=1000)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    
    # Expiry
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.organization.name}"
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = f"sk_{secrets.token_urlsafe(32)}"
            self.key_preview = self.key[:8] + '...'
        super().save(*args, **kwargs)

class Notification(models.Model):
    """User notifications system"""
    TYPE_CHOICES = (
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='notifications')
    
    # Notification content
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    
    # Status
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    
    # Actions
    action_url = models.URLField(blank=True)
    action_text = models.CharField(max_length=100, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['organization', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

class ActivityLog(models.Model):
    """Track user and system activities"""
    ACTION_CHOICES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('view', 'View'),
        ('export', 'Export'),
        ('import', 'Import'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='activity_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs', null=True, blank=True)
    
    # Activity details
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    
    # Request details
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'created_at']),
            models.Index(fields=['user', 'action']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]
    
    def __str__(self):
        return f"{self.action} {self.resource_type} by {self.user or 'System'}"
