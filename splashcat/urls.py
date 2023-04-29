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
from django.urls import path, include
from django.views.generic import TemplateView

import users.views as users_views
from splashcat import settings

urlpatterns = [
    path('', TemplateView.as_view(template_name='splashcat/home.html'), name='home'),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
    path('users/', include('users.urls')),
    path('battles/', include('battles.urls')),
    path('@<str:username>/', users_views.profile, name='profile'),
    path('sponsor/', TemplateView.as_view(template_name='splashcat/sponsor.html'), name='sponsor'),
    path('i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # let web server handle this in production
    urlpatterns += static('api/schemas/', document_root=settings.BASE_DIR / 'battles/format_schemas/')
