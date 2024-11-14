"""
URL configuration for splashcat project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import views
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from strawberry.django.views import AsyncGraphQLView

import users.views as users_views
from battles.sitemaps import BattlesSitemap, BattleGroupsSitemap
from django.conf import settings

from indexnow.views import indexnow_api_key
from splashcat.oidc_provider_settings import openid_auth
from splashcat.schema import schema
from splashcat.sitemaps import StaticViewSitemap
from splashcat.views import home, sponsor, uploaders_information, health_check, robots_txt, legal, ads_txt, about
from users.sitemaps import UsersSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'users': UsersSitemap,
    'battles': BattlesSitemap,
    'battle-groups': BattleGroupsSitemap,
}

urlpatterns = [
    path('', home, name='home'),
    path('graphql', csrf_exempt(openid_auth(AsyncGraphQLView.as_view(schema=schema, graphql_ide="apollo-sandbox")))),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
    path('unicorn/', include('django_unicorn.urls')),
    path('users/', include('users.urls')),
    path('groups/', include('groups.urls')),
    path('battles/', include('battles.urls')),
    path('videos/', include('videos.urls')),
    path('search/', include('search.urls')),
    path('assistant/', include('assistant.urls')),
    path('embeds/', include('embed_images.urls')),
    path('sponsors/', include('sponsors.urls')),
    path('@<str:username>/', users_views.profile, name='profile'),
    path('@<str:username>.json', users_views.profile_json, name='profile_json'),
    path('@<str:username>/battles/', users_views.profile_battle_list, name='profile_battles_list'),
    path('@<str:username>/album/', users_views.profile_album, name='profile_album'),
    path('@<str:username>/followers/', users_views.profile_follows, {'view_type': 'followers'}, name='profile_followers'),
    path('@<str:username>/following/', users_views.profile_follows, {'view_type': 'following'}, name='profile_following'),
    path('set_user_timezone/', users_views.set_user_timezone, name='set_user_timezone'),
    path('follow/<str:username>/', users_views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', users_views.unfollow_user, name='unfollow_user'),
    path('notifications/mark-read/', users_views.mark_notifications_as_read, name='mark_notifications_as_read'),
    path('notifications/fetch/', users_views.get_notifications, name='fetch_notifications'),
    path('sponsor/', sponsor, name='sponsor'),
    path('legal/', legal, name='legal'),
    path('about/', about, name='about'),
    path('uploaders-information/', uploaders_information, name='uploaders_information'),
    path('health-check/', health_check, name='health_check'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('openid/', include('oidc_provider.urls', namespace='oidc_provider')),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('ads.txt', ads_txt, name='ads_txt'),
    path(f'{settings.INDEXNOW_API_KEY}.txt', indexnow_api_key, name='indexnow_api_key'),
    # path('silk/', include('silk.urls', namespace='silk')),
    path(
        "sitemap.xml",
        views.index,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.index",
    ),
    path(
        "sitemap-<section>.xml",
        views.sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # let web server handle this in production
    urlpatterns += static('api/schemas/', document_root=settings.BASE_DIR / 'battles/format_schemas/')
