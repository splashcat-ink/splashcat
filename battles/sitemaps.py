from django.contrib.sitemaps import Sitemap

from battles.models import Battle


class BattlesSitemap(Sitemap):
    def items(self):
        return Battle.objects.exclude(vs_mode=Battle.VsMode.PRIVATE)

    @staticmethod
    def lastmod(obj: Battle):
        return obj.updated_at
