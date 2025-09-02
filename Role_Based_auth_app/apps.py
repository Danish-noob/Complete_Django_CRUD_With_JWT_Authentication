from django.apps import AppConfig


class RoleBasedAuthAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Role_Based_auth_app'
    
    def ready(self):
        import Role_Based_auth_app.signals  # noqa
