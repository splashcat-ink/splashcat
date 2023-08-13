from django.contrib.sitemaps import Sitemap

from users.models import User


class UsersSitemap(Sitemap):
    protocol = 'https'
    
    def items(self):
        return User.objects.all()
