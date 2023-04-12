from django.db import models


# Create your models here.


class Image(models.Model):
    """
    Represents a SplatNet asset image that has been saved by Splashcat.
    """
    image = models.ImageField(upload_to='splatnet_assets/')
    type = models.CharField(max_length=50)  # e.g. "weapon", "stage", "headgear", etc.
    asset_name = models.CharField(max_length=100)  # weapon id, stage id, etc.
    original_file_name = models.CharField(max_length=100)

    def __str__(self):
        return self.image.name
