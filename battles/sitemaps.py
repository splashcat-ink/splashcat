from django.contrib.sitemaps import Sitemap

from battles.models import Battle, BattleGroup


class BattlesSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        return Battle.objects.exclude(vs_mode=Battle.VsMode.PRIVATE)

    @staticmethod
    def lastmod(obj: Battle):
        return obj.updated_at


class BattleGroupsSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        return BattleGroup.objects.all()
