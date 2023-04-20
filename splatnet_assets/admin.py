from django.contrib import admin

from splatnet_assets.models import *

# Register your models here.

admin.site.register(Image)


class LocalizationStringAdmin(admin.ModelAdmin):
    list_display = ('internal_id', 'type', 'string_en_us')
    list_filter = ('type',)


admin.site.register(LocalizationString, LocalizationStringAdmin)

admin.site.register(Gear)
admin.site.register(Brand)
admin.site.register(Ability)
admin.site.register(NameplateBackground)
admin.site.register(NameplateBadge)
admin.site.register(Award)
admin.site.register(Stage)
admin.site.register(Weapon)
admin.site.register(SubWeapon)
admin.site.register(SpecialWeapon)
admin.site.register(TitleAdjective)
admin.site.register(TitleSubject)
