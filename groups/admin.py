# Register your models here.
from django.contrib import admin

from groups.models import Group, Membership


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    inlines = [MembershipInline]
