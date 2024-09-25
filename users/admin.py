from django import forms
from django.contrib import admin
from django.contrib.admin import TabularInline
from django.contrib.auth.admin import UserAdmin as AbstractUserAdmin

from groups.admin import MembershipInline
from .models import User, ApiKey, GitHubLink, ProfileUrl, Follow


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


class FollowerForm(forms.ModelForm):
    class Meta:
        model = Follow
        fields = ['follower', 'followed']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['follower'].queryset = User.objects.all()
        self.fields['followed'].queryset = User.objects.all()

class FollowingInline(TabularInline):
    model = Follow
    fk_name = 'follower'
    fields = ('followed', 'followed_on')
    readonly_fields = ('followed_on',)
    extra = 0
    can_delete = True
    verbose_name = "Following"
    verbose_name_plural = "Following"

class FollowersInline(TabularInline):
    model = Follow
    fk_name = 'followed'
    fields = ('follower', 'followed_on')
    readonly_fields = ('followed_on',)
    extra = 0
    can_delete = True
    verbose_name = "Follower"
    verbose_name_plural = "Followers"

class UserAdmin(AbstractUserAdmin):
    fieldsets = AbstractUserAdmin.fieldsets + (
        (None, {"fields": ["profile_picture", "saved_favorite_color", "data_export_pending", 
                           "last_data_export", "verified_email", "preferred_pronouns", 
                           "approved_to_upload_videos", "video_collection_id", 
                           "coral_friend_url", "stripe_customer_id", "_stripe_entitlements"]}),
    )
    inlines = [GitHubLinkInline, MembershipInline, UrlInline, FollowingInline, FollowersInline]
    list_display = ("username", "display_name", "email", "is_staff", "date_joined", "verified_email")
    search_fields = ("username", "display_name", "email")

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.fieldsets[1][1]["fields"] = ("display_name", "email")

class FollowerAdmin(admin.ModelAdmin):
    form = FollowerForm
    list_display = ('follower', 'followed', 'followed_on')
    search_fields = ('follower__username', 'followed__username')
    list_filter = ('followed_on',)

admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowerAdmin)
admin.site.register(ApiKey)
admin.site.register(GitHubLink)
