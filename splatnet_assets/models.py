from django.db import models
from django.utils.translation import get_language


# Create your models here.


class Image(models.Model):
    """
    Represents a SplatNet asset image that has been saved by Splashcat.
    """
    image = models.ImageField(upload_to='splatnet_assets/')
    type = models.CharField(max_length=50)  # e.g. "weapon", "stage", "headgear", etc.
    asset_name = models.CharField(max_length=100)  # weapon id, stage id, etc.
    original_file_name = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.image.name


class LocalizationString(models.Model):
    class Type(models.TextChoices):
        OTHER = 'OTHER', 'Other'
        WEAPON_NAME = 'WEAPON_NAME', 'Weapon Name'
        SUB_WEAPON_NAME = 'SUB_WEAPON_NAME', 'Sub Weapon Name'
        SPECIAL_WEAPON_NAME = 'SPECIAL_WEAPON_NAME', 'Special Weapon Name'
        TITLE_ADJECTIVE = 'TITLE_ADJECTIVE', 'Title Adjective'
        TITLE_SUBJECT = 'TITLE_SUBJECT', 'Title Subject'
        HEAD_GEAR = 'HEAD_GEAR', 'Head Gear'
        CLOTHING_GEAR = 'CLOTHING_GEAR', 'Clothing Gear'
        SHOES_GEAR = 'SHOES_GEAR', 'Shoes Gear'
        ABILITY = 'ABILITY', 'Ability'
        ABILITY_DESCRIPTION = 'ABILITY_DESCRIPTION', 'Ability Description'
        BRAND = 'BRAND', 'Brand'
        STAGE = 'STAGE', 'Stage'

    internal_id = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=Type.choices)
    string_de_de = models.TextField(blank=True)
    string_en_gb = models.TextField(blank=True)
    string_en_us = models.TextField(blank=True)
    string_es_es = models.TextField(blank=True)
    string_es_mx = models.TextField(blank=True)
    string_fr_ca = models.TextField(blank=True)
    string_fr_fr = models.TextField(blank=True)
    string_it_it = models.TextField(blank=True)
    string_ja_jp = models.TextField(blank=True)
    string_ko_kr = models.TextField(blank=True)
    string_nl_nl = models.TextField(blank=True)
    string_ru_ru = models.TextField(blank=True)
    string_zh_cn = models.TextField(blank=True)
    string_zh_tw = models.TextField(blank=True)

    def get_localized(self, locale: str = None):
        if locale is None:
            locale = get_language()
        string = getattr(self, f'string_{locale.lower().replace("-", "_")}')
        if string is None or string == '':
            string = self.string_en_us
        return string

    def __str__(self):
        return f'{self.type} {self.internal_id} "{self.string_en_us}"'


class Gear(models.Model):
    class GearType(models.TextChoices):
        HEAD = 'HEAD', 'Head'
        CLOTHING = 'CLOTHING', 'Clothing'
        SHOES = 'SHOES', 'Shoes'

    internal_id = models.CharField(max_length=100)
    name = models.OneToOneField('LocalizationString', on_delete=models.PROTECT)
    type = models.CharField(max_length=50, choices=GearType.choices)
    brand = models.ForeignKey('Brand', on_delete=models.PROTECT)
    rarity = models.IntegerField()
    main_ability = models.ForeignKey('Ability', on_delete=models.PROTECT)
    image = models.OneToOneField('Image', on_delete=models.PROTECT, related_name='+')

    def __str__(self):
        return f'{self.name.string_en_us} ({self.type})'


class Ability(models.Model):
    class Meta:
        verbose_name_plural = 'abilities'

    internal_id = models.CharField(max_length=100)
    name = models.OneToOneField('LocalizationString', on_delete=models.PROTECT)
    image = models.OneToOneField('Image', on_delete=models.PROTECT, related_name='+')
    description = models.OneToOneField('LocalizationString', on_delete=models.PROTECT, related_name='+')

    def __str__(self):
        return f'{self.internal_id} - {self.name.string_en_us}'


class Brand(models.Model):
    internal_id = models.CharField(max_length=100)
    name = models.OneToOneField('LocalizationString', on_delete=models.PROTECT)
    image = models.OneToOneField('Image', on_delete=models.PROTECT, related_name='brand')
    favored_ability = models.ForeignKey('Ability', on_delete=models.PROTECT, related_name='+')
    unfavored_ability = models.ForeignKey('Ability', on_delete=models.PROTECT, related_name='+')

    def __str__(self):
        return f'{self.internal_id} - {self.name.string_en_us}'


class NameplateBackground(models.Model):
    pass


class NameplateBadge(models.Model):
    pass


class Stage(models.Model):
    pass


class Award(models.Model):
    pass


class Weapon(models.Model):
    pass


class SubWeapon(models.Model):
    pass


class SpecialWeapon(models.Model):
    pass
