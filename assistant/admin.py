from django.contrib import admin

from assistant.models import Thread, SharedThread

# Register your models here.

admin.site.register(Thread)
admin.site.register(SharedThread)
