from django import forms

from groups.models import Group


class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = (
            "name",
            "description",
            "privacy_level",
        )


class GroupInviteForm(forms.Form):
    username = forms.CharField(max_length=255)
