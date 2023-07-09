from oidc_provider.apps import OIDCProviderConfig


class PatchedOidcProvider(OIDCProviderConfig):
    default_auto_field = 'django.db.models.AutoField'
