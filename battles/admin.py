from django.contrib import admin

from .models import Battle, UnprocessedBattle

# Register your models here.

admin.site.register(Battle)
admin.site.register(UnprocessedBattle)
