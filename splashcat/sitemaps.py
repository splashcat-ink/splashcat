from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    def items(self):
        return ["home", "sponsor"]

    def location(self, item):
        return reverse(item)
