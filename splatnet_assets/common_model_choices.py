from django.db import models
from django.utils.translation import gettext_lazy as _


class XBattleDivisions(models.TextChoices):
    UNSPECIFIED = 'UNSPECIFIED', _('Unspecified')
    TENTATEK = 'TENTATEK', _('Tentatek')
    TAKOROKA = 'TAKOROKA', _('Takoroka')
