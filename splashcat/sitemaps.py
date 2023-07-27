from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    def items(self):
        return ["home", "sponsor", "uploaders_information", "users:login", "users:register"]

    def location(self, item):
        return reverse(item)
