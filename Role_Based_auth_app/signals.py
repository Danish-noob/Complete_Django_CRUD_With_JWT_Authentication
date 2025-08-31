from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Category, Product
from django.utils.text import slugify



@receiver(pre_save, sender=Category)
def ensure_category_slug(sender, instance: Category, **kwargs):
	if not instance.slug:
		instance.slug = slugify(instance.name)



@receiver(pre_save, sender=Product)
def ensure_product_slug(sender, instance: Product, **kwargs):
	if not instance.slug and (instance.name or instance.product_name):
		instance.slug = slugify(instance.name or instance.product_name)

