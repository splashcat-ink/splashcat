from datetime import timedelta

from django import template

register = template.Library()


@register.filter
def duration(value: timedelta):
    # format the value as "M:SS", for example: "3:45"
    return f"{value.seconds // 60}:{value.seconds % 60:02d}"
