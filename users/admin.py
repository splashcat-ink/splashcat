from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AbstractUserAdmin

from .models import User


class UserAdmin(AbstractUserAdmin):
    fieldsets = AbstractUserAdmin.fieldsets + (
    (None, {"fields": ["profile_picture", "is_splashcat_sponsor", "is_sponsor_public"]}),)

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.fieldsets[1][1]["fields"] = ("display_name", "email")


admin.site.register(User, UserAdmin)
