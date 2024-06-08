from django.db import models

from users.models import User


# Create your models here.

class StatInkImport(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='private/statink_importer/imports/')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
