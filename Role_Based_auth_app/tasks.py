from celery import shared_task
from django.utils import timezone
from django.db.models import Sum
from .models import Usage, Subscription, Organization



@shared_task
def calculate_monthly_usage():
	now = timezone.now()
	start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
	end = now
	# Rollup example: sum API calls per org (assuming a 'api_calls' feature)
	for org in Organization.objects.filter(is_active=True):
		qs = Usage.objects.filter(organization=org, feature='api_calls', period_start__gte=start, period_end__lte=end)
		total = qs.aggregate(total=Sum('count'))['total'] or 0
		Usage.objects.update_or_create(
			organization=org,
			feature='api_calls_monthly',
			period_start=start,
			defaults={'period_end': end, 'count': total, 'limit': None}
		)