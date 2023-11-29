from django.db import models


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
