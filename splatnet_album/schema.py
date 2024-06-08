import re

import requests
import strawberry
import strawberry_django
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
from graphql import GraphQLError
from strawberry.types import Info
from strawberry_django.auth.utils import get_current_user
from strawberry_django.permissions import IsAuthenticated
from strawberry import relay
from strawberry_django.relay import ListConnectionWithTotalCount

from splatnet_album import models
from splatnet_album.types import AlbumImage
from users.models import User


@strawberry.type(name="Query")
class SplatNetAlbumQuery:
    userAlbum: ListConnectionWithTotalCount[AlbumImage] = strawberry_django.connection()


def check_url(url):
    pattern = r'https://storage\.googleapis\.com/ugcstore-toyohr-lp1-persistent/npln_ugcstore_toyohr_lp1/'
    match = re.search(pattern, url)
    if match is None:
        raise GraphQLError('URL isn\'t a valid NPLN UGC store URL. Are you sure it\'s from SplatNet 3?')


def get_image_id(url):
    pattern = r"https://storage\.googleapis\.com/ugcstore-toyohr-lp1-persistent/npln_ugcstore_toyohr_lp1/(\w+)\?"
    match = re.search(pattern, url)
    if match is None:
        raise GraphQLError('URL isn\'t a valid NPLN UGC store URL. Are you sure it\'s from SplatNet 3?')
    return match.group(1)


@strawberry.type(name="Mutation")
class SplatNetAlbumMutation:
    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    def upload_album_image(self, splatnet_url: str, info: Info) -> AlbumImage:
        current_user: User = get_current_user(info)

        check_url(splatnet_url)

        image_response = requests.get(splatnet_url)
        image_content = ContentFile(image_response.content)

        album_image = models.AlbumImage(
            npln_image_id=get_image_id(splatnet_url),
            user=current_user,
            splatnet_url=splatnet_url,
        )
        album_image.image.save(f"{current_user.username}/{get_random_string(30)}.jpg", image_content)

        album_image.save()

        return album_image
