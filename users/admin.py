from django.contrib import admin
from django.contrib.admin import TabularInline
from django.contrib.auth.admin import UserAdmin as AbstractUserAdmin

from groups.admin import MembershipInline
from .models import User, ApiKey, GitHubLink, ProfileUrl


class ApiKeyInline(TabularInline):
    model = ApiKey
    fields = ("key", "created", "note")
    readonly_fields = ("key", "created")
    extra = 0
    can_delete = True
    verbose_name = "API Key"
    verbose_name_plural = "API Keys"


class GitHubLinkInline(TabularInline):
    model = GitHubLink
    fields = ('github_id', 'github_username', 'is_sponsor', 'is_sponsor_public', 'sponsorship_amount_usd')


class UrlInline(TabularInline):
    model = ProfileUrl
    fields = ('url', 'is_rel_me_verified')


class UserAdmin(AbstractUserAdmin):
    fieldsets = AbstractUserAdmin.fieldsets + (
        (None, {"fields": ["profile_picture", "saved_favorite_color", "data_export_pending", "last_data_export",
                           "verified_email", "preferred_pronouns", "approved_to_upload_videos",
                           "video_collection_id"]}),)
    inlines = [GitHubLinkInline, MembershipInline, UrlInline]
    list_display = ("username", "display_name", "email", "is_staff", "date_joined", "verified_email",)
    search_fields = ("username", "display_name", "email")

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.fieldsets[1][1]["fields"] = ("display_name", "email")


admin.site.register(User, UserAdmin)
admin.site.register(ApiKey)
admin.site.register(GitHubLink)
