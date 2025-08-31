
from django.utils.deprecation import MiddlewareMixin



class APIAnalyticsMiddleware(MiddlewareMixin):
	"""Simple request analytics + ActivityLog capture for mutating requests."""
	import re
	SENSITIVE_PATHS = re.compile(r"/api/auth/|/admin/")

	def process_response(self, request, response):
		try:
			if request.method in ("POST", "PUT", "PATCH", "DELETE") and not self.SENSITIVE_PATHS.search(request.path):
				from Role_Based_auth_app.models import ActivityLog
				ActivityLog.objects.create(
					organization=getattr(request, 'organization', None),
					user=getattr(request, 'user', None) if getattr(request, 'user', None) and request.user.is_authenticated else None,
					action=self._method_to_action(request.method),
					resource_type='API',
					resource_id=None,
					description=f"{request.method} {request.path}",
					ip_address=self._get_ip(request),
					user_agent=request.META.get('HTTP_USER_AGENT', ''),
					request_path=request.path,
					request_method=request.method,
					metadata={"status_code": response.status_code},
				)
		except Exception:
			# Fail-safe: never block request due to analytics error
			pass
		return response



	@staticmethod
	def _method_to_action(method: str) -> str:
		return {
			'POST': 'create',
			'PUT': 'update',
			'PATCH': 'update',
			'DELETE': 'delete',
		}.get(method, 'view')

	@staticmethod
	def _get_ip(request):
		x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
		if x_forwarded_for:
			ip = x_forwarded_for.split(',')[0]
		else:
			ip = request.META.get('REMOTE_ADDR')
		return ip


