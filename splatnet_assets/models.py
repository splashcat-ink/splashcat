from django.db import models
from django.utils.translation import get_language
from django_choices_field import TextChoicesField

from splatnet_assets.fields import ColorField


# Create your models here.


class Image(models.Model):
    """
    Represents a SplatNet asset image that has been saved by Splashcat.
    """
    image = models.ImageField(upload_to='splatnet_assets/')
    type = models.CharField(max_length=50)  # e.g. "weapon", "stage", "headgear", etc.
    asset_name = models.CharField(max_length=100)  # weapon id, stage id, etc.
    original_file_name = models.CharField(max_length=500, blank=True)
    width = models.PositiveIntegerField(default=0)
    height = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.image.name

    @property
    def url(self):
        return self.image.url


django_locale_to_splatnet_locale = {
    'ja': 'ja-JP',
    'es': 'es-ES',
    'ru': 'ru-RU',
}


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
        BADGE_DESCRIPTION = 'BADGE_DESCRIPTION', 'Badge Description'
        AWARD = 'AWARD', 'Award'
        BRAND = 'BRAND', 'Brand'
        STAGE = 'STAGE', 'Stage'
        CHALLENGE_NAME = 'CHALLENGE_NAME', 'Challenge Name'
        CHALLENGE_DESCRIPTION = 'CHALLENGE_DESCRIPTION', 'Challenge Description'
        CHALLENGE_LONG_DESCRIPTION = 'CHALLENGE_LONG_DESCRIPTION', 'Challenge Long Description'

    internal_id = models.CharField(max_length=100)
    type = TextChoicesField(choices_enum=Type)
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

    @property
    def string(self):
        return self.get_string()

    def get_string(self, locale: str = None):
        if locale is None:
            locale = get_language()

        if locale in django_locale_to_splatnet_locale:
            locale = django_locale_to_splatnet_locale[locale]

        # Handle locales that don't exist
        exists = hasattr(self, f'string_{locale.lower().replace("-", "_")}')
        if not exists:
            locale = 'en-us'
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
    type = TextChoicesField(choices_enum=GearType)
    brand = models.ForeignKey('Brand', on_delete=models.PROTECT)
    rarity = models.IntegerField()
    main_ability = models.ForeignKey('Ability', on_delete=models.PROTECT)
    image = models.ForeignKey('Image', on_delete=models.PROTECT, related_name='+')

    def __str__(self):
        return f'{self.name.internal_id} ({self.type})'


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
    internal_id = models.CharField(max_length=100)
    splatnet_id = models.IntegerField()
    image = models.OneToOneField('Image', on_delete=models.PROTECT, related_name='+')
    text_color = ColorField()


class NameplateBadge(models.Model):
    internal_id = models.CharField(max_length=100)
    splatnet_id = models.IntegerField()
    image = models.OneToOneField('Image', on_delete=models.PROTECT, related_name='+')
    description = models.ForeignKey('LocalizationString', on_delete=models.PROTECT)

    @property
    def translated_description(self):
        from splatnet_assets.badge_descriptions import get_proper_badge_localization
        return get_proper_badge_localization(self)


class Stage(models.Model):
    internal_id = models.CharField(max_length=100)
    splatnet_id = models.IntegerField()
    name = models.ForeignKey('LocalizationString', on_delete=models.PROTECT)
    image = models.ForeignKey('Image', on_delete=models.PROTECT, related_name='+')
    image_banner = models.ForeignKey('Image', on_delete=models.PROTECT, related_name='+')

    def __str__(self):
        return f'{self.internal_id} - {self.name.string_en_us}'


class Award(models.Model):
    internal_id = models.CharField(max_length=100)
    name = models.OneToOneField('LocalizationString', on_delete=models.PROTECT)
    gold = models.BooleanField()

    def __str__(self):
        return f'{self.internal_id} - {self.name.string_en_us}'


class TitleAdjective(models.Model):
    internal_id = models.CharField(max_length=100)
    string = models.OneToOneField('LocalizationString', on_delete=models.PROTECT)


class TitleSubject(models.Model):
    internal_id = models.CharField(max_length=100)
    string = models.OneToOneField('LocalizationString', on_delete=models.PROTECT)


class Weapon(models.Model):
    internal_id = models.CharField(max_length=100)
    splatnet_id = models.IntegerField()
    name = models.OneToOneField('LocalizationString', on_delete=models.PROTECT)
    sub = models.ForeignKey('SubWeapon', on_delete=models.PROTECT)
    special = models.ForeignKey('SpecialWeapon', on_delete=models.PROTECT)
    flat_image = models.OneToOneField('Image', on_delete=models.PROTECT, related_name='+')
    image_3d = models.OneToOneField('Image', on_delete=models.PROTECT, related_name='+')


class SubWeapon(models.Model):
    internal_id = models.CharField(max_length=100)
    splatnet_id = models.IntegerField()
    name = models.OneToOneField('LocalizationString', on_delete=models.PROTECT)
    image = models.OneToOneField('Image', on_delete=models.PROTECT, related_name='+')
    mask_image = models.OneToOneField('Image', on_delete=models.PROTECT, related_name='+')
    overlay_image = models.OneToOneField('Image', on_delete=models.PROTECT, related_name='+')


class SpecialWeapon(models.Model):
    internal_id = models.CharField(max_length=100)
    splatnet_id = models.IntegerField()
    name = models.OneToOneField('LocalizationString', on_delete=models.PROTECT)
    image = models.OneToOneField('Image', on_delete=models.PROTECT, related_name='+')
    mask_image = models.OneToOneField('Image', on_delete=models.PROTECT, related_name='+')
    overlay_image = models.OneToOneField('Image', on_delete=models.PROTECT, related_name='+')


class Challenge(models.Model):
    internal_id = models.CharField(max_length=100)
    name = models.OneToOneField('LocalizationString', on_delete=models.PROTECT, related_name='+')
    description = models.OneToOneField('LocalizationString', on_delete=models.PROTECT, related_name='+')
    long_description = models.OneToOneField('LocalizationString', on_delete=models.PROTECT, related_name='+')


class Splatfest(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['start_date', 'end_date']),
        ]

    internal_id = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    team_1_color = ColorField()
    team_2_color = ColorField()
    team_3_color = ColorField()
