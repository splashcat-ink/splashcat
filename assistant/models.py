from django.db import models


# Create your models here.

class Thread(models.Model):
    creator = models.ForeignKey('users.User', on_delete=models.CASCADE)
    openai_thread_id = models.CharField(max_length=255)
    openai_file_id = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
