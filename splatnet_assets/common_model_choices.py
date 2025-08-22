from django.db import models
from django.utils.translation import gettext_lazy as _


class XBattleDivisions(models.TextChoices):
    UNSPECIFIED = 'UNSPECIFIED', _('Unspecified')
    TENTATEK = 'TENTATEK', _('Tentatek')
    TAKOROKA = 'TAKOROKA', _('Takoroka')


class PlayerNameShown(models.TextChoices):
    ALWAYS = 'ALWAYS', _('Always')
    PRIVATE_BATTLES = 'PRIVATE_BATTLES', _('Only in private battles')
    PUBLIC_BATTLES = 'PUBLIC_BATTLES', _('Only in public battles')
    NEVER = 'NEVER', _('Never')
