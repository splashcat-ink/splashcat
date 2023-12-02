import re

from django import template

register = template.Library()

regex = r"{{ruby .*?}}"


@register.filter
def strip_ruby(title: str):
    return re.sub(regex, "", title)
