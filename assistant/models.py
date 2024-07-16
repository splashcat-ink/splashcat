import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse


# Create your models here.

class Thread(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CREATED = 'CREATED', 'Created'

    creator = models.ForeignKey('users.User', on_delete=models.CASCADE)
    openai_thread_id = models.CharField(max_length=255)
    openai_file_id = models.CharField(max_length=255, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    initial_message = models.TextField(default='')
    status = models.CharField(blank=True, choices=Status.choices, max_length=25)
    runner_machine_id = models.CharField(blank=True, max_length=20)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def get_absolute_url(self):
        return reverse('assistant:view_thread', args=[str(self.id)])

    def __str__(self):
        return f"Thread {self.id} - {self.openai_thread_id} - @{self.creator.username}"


class SharedThread(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True, unique=True)
    creator = models.ForeignKey('users.User', on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    data = models.JSONField()

    def get_absolute_url(self):
        return reverse('assistant:view_shared_thread', args=[str(self.uuid)])
