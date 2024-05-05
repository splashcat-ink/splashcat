from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    protocol = 'https'

    def items(self):
        return ["home",
                "sponsor",
                "uploaders_information",
                "users:login",
                "users:register",
                "legal",
                "about",
                ]

    def location(self, item):
        return reverse(item)
