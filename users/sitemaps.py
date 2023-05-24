from django.contrib.sitemaps import Sitemap

from users.models import User


class UsersSitemap(Sitemap):
    def items(self):
        return User.objects.all()
