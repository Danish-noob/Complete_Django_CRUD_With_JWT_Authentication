from django.contrib import admin
from .models import Organization, User, Category, Product, ProductImage, Subscription, Usage, FileUpload, APIKey

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
	list_display = ("name", "slug", "domain", "plan", "is_active", "created_at")
	search_fields = ("name", "slug", "domain")
	list_filter = ("plan", "is_active")

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ("username", "email", "role", "organization", "is_active", "last_login")
	list_filter = ("role", "is_active", "organization")
	search_fields = ("username", "email", "first_name", "last_name")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ("name", "slug", "organization", "is_active", "sort_order")

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
	model = ProductImage


# Remove duplicate admin registrations for Product, Subscription, FileUpload, and APIKey. Keep only one registration per model.

class ProductImageInline(admin.TabularInline):
	model = ProductImage
	extra = 0
