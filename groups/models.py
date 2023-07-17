from django.db import models
from django.urls import reverse


# Create your models here.

class Group(models.Model):
    class PrivacyLevels(models.TextChoices):
        PUBLIC = 'PUBLIC', 'Public'
        RESTRICTED = 'RESTRICTED', 'Restricted'
        PRIVATE = 'PRIVATE', 'Private'

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    members = models.ManyToManyField('users.User', through='Membership')
    owner = models.ForeignKey('users.User', related_name='groups_owned', on_delete=models.CASCADE)
    pending_invites = models.ManyToManyField('users.User', related_name='pending_group_invites', blank=True)
    pending_join_requests = models.ManyToManyField('users.User', related_name='pending_group_join_requests', blank=True)
    privacy_level = models.CharField(max_length=20, choices=PrivacyLevels.choices, default=PrivacyLevels.PUBLIC)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('groups:view_group', kwargs={'group_id': self.pk})


class Membership(models.Model):
    person = models.ForeignKey('users.User', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date_joined = models.DateField(auto_now_add=True)
