from django.db import models


# Create your models here.


class Battle(models.Model):
    uploader = models.ForeignKey('users.User', on_delete=models.CASCADE)
    splatnet_id = models.CharField(max_length=32)
    raw_data = models.JSONField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Battle {self.id} ({self.splatnet_id}) - @{self.uploader.username}'
