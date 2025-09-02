from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (Organization, User, Category, Product, ProductImage, 
                     Subscription, Usage, FileUpload, APIKey, Notification, ActivityLog)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "domain", "plan", "is_active", "created_at")
    search_fields = ("name", "slug", "domain")
    list_filter = ("plan", "is_active", "created_at")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "organization", "is_active", "last_login")
    list_filter = ("role", "is_active", "organization", "is_email_verified")
    search_fields = ("username", "email", "first_name", "last_name")
    readonly_fields = ("id", "created_at", "updated_at", "last_login", "date_joined")
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Organization', {'fields': ('organization', 'role')}),
        ('Profile', {'fields': ('avatar', 'phone', 'bio', 'timezone', 'language')}),
        ('Verification', {'fields': ('is_email_verified', 'two_factor_enabled')}),
        ('Activity', {'fields': ('last_activity', 'login_count', 'notifications_enabled')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "organization", "is_active", "sort_order")
    list_filter = ("is_active", "organization")
    search_fields = ("name", "slug")
    readonly_fields = ("id", "created_at", "updated_at")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    readonly_fields = ("id", "created_at")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_name", "organization", "category", "price", "quantity", "is_active")
    list_filter = ("is_active", "is_featured", "is_digital", "organization", "category")
    search_fields = ("product_name", "name", "sku", "description")
    readonly_fields = ("id", "sku", "view_count", "rating", "review_count", "created_at", "updated_at")
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_name', 'name', 'slug', 'organization', 'category', 'description', 'short_description')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'sale_price', 'cost_price', 'quantity', 'sku')
        }),
        ('Status & Visibility', {
            'fields': ('is_active', 'is_featured', 'is_digital')
        }),
        ('SEO & Metadata', {
            'fields': ('meta_title', 'meta_description', 'tags')
        }),
        ('Tracking', {
            'fields': ('view_count', 'rating', 'review_count')
        }),
        ('User Tracking', {
            'fields': ('created_by', 'updated_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "alt_text", "is_primary", "sort_order")
    list_filter = ("is_primary", "product__organization")
    search_fields = ("product__product_name", "alt_text")
    readonly_fields = ("id", "created_at")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("organization", "plan", "status", "current_period_end", "is_active")
    list_filter = ("plan", "status", "cancel_at_period_end")
    search_fields = ("organization__name", "stripe_customer_id")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Usage)
class UsageAdmin(admin.ModelAdmin):
    list_display = ("organization", "feature", "count", "limit", "usage_percentage")
    list_filter = ("feature", "organization")
    search_fields = ("organization__name", "feature")
    readonly_fields = ("id", "usage_percentage", "is_limit_exceeded", "created_at", "updated_at")


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ("original_name", "organization", "uploaded_by", "file_type", "file_size_formatted")
    list_filter = ("file_type", "is_public", "organization")
    search_fields = ("original_name", "organization__name", "uploaded_by__username")
    readonly_fields = ("id", "file_size", "file_size_formatted", "download_count", "created_at", "updated_at")


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "created_by", "is_active", "last_used", "is_expired")
    list_filter = ("is_active", "organization")
    search_fields = ("name", "organization__name", "created_by__username")
    readonly_fields = ("id", "key", "key_preview", "usage_count", "is_expired", "created_at", "updated_at")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "organization", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "organization")
    search_fields = ("title", "message", "user__username")
    readonly_fields = ("id", "created_at", "read_at")


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("action", "resource_type", "user", "organization", "created_at")
    list_filter = ("action", "resource_type", "organization")
    search_fields = ("description", "user__username", "resource_type")
    readonly_fields = ("id", "created_at")
    
    def has_add_permission(self, request):
        return False  # Activity logs should only be created programmatically
    
    def has_change_permission(self, request, obj=None):
        return False  # Activity logs should be immutable
