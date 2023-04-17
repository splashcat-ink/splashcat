from django.contrib import admin
from django.contrib.admin import TabularInline
from django.contrib.auth.admin import UserAdmin as AbstractUserAdmin

from .models import User, ApiKey


class ApiKeyInline(TabularInline):
    model = ApiKey
    fields = ("key", "created", "note")
    readonly_fields = ("key", "created")
    extra = 0
    can_delete = True
    verbose_name = "API Key"
    verbose_name_plural = "API Keys"


class UserAdmin(AbstractUserAdmin):
    fieldsets = AbstractUserAdmin.fieldsets + (
        (None, {"fields": ["profile_picture", "is_splashcat_sponsor", "is_sponsor_public"]}),)
    inlines = [ApiKeyInline]

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.fieldsets[1][1]["fields"] = ("display_name", "email")


admin.site.register(User, UserAdmin)
admin.site.register(ApiKey)
