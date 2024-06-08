from django.db import models

from users.models import User


# Create your models here.


class AlbumImage(models.Model):
    splatnet_url = models.URLField(unique=True, max_length=750)
    npln_image_id = models.CharField(max_length=50)
    image = models.ImageField(upload_to='splatnet_album/images/', height_field='height', width_field='width')
    height = models.IntegerField()
    width = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
