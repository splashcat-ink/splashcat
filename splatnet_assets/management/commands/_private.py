from io import BytesIO
from PIL import Image as PillowImage

import requests
from django.core.files.base import ContentFile

from splatnet_assets.models import Image


def get_latest_version():
    version_data_url = 'https://leanny.github.io/splat3/versions.json'
    return requests.get(version_data_url).json()[-1]


def download_image(asset_type: str, asset_name: str, asset_url: str) -> Image:
    print(f'Downloading {asset_url}...')
    response = requests.get(asset_url)
    image_data = BytesIO(response.content)

    image, _created = Image.objects.get_or_create(type=asset_type, asset_name=str(asset_name))

    if response.ok:
        with PillowImage.open(image_data) as pillow_image:
            width, height = pillow_image.size
            image.width = width
            image.height = height
    else:
        image.width = 0
        image.height = 0

    image.original_file_name = asset_url
    if image.image:
        image.image.delete()
    image.image.save(f'{asset_type}/{asset_name}.{asset_url.split(".")[-1]}', ContentFile(image_data.getvalue()))

    image.save()

    return image


def download_image_from_path(asset_type: str, asset_name: str, asset_path: str) -> Image:
    prefix = 'https://leanny.github.io/splat3/images/'
    return download_image(asset_type, asset_name, f'{prefix}{asset_path}')
