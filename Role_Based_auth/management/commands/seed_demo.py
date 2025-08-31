from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from Role_Based_auth_app.models import Organization, Category, Product


User = get_user_model()


class Command(BaseCommand):
	help = "Seed demo data for local development"

	def handle(self, *args, **options):
		org, _ = Organization.objects.get_or_create(name='Demo Org', slug='demo', defaults={'plan': 'pro'})
		owner, _ = User.objects.get_or_create(username='owner', defaults={'email': 'owner@example.com', 'organization': org, 'role': 'owner'})
		owner.set_password('owner1234')
		owner.save()
		cat, _ = Category.objects.get_or_create(organization=org, name='General', slug='general')
		for i in range(1, 6):
			Product.objects.get_or_create(
				product_name=f"Demo Product {i}",
				organization=org,
				defaults={'price': 100 + i, 'quantity': 10 * i}
			)
		self.stdout.write(self.style.SUCCESS('Seeded demo data.'))