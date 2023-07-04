from django import template

register = template.Library()


@register.filter
def format_power(value: float):
    # round down to the first decimal place
    value = int(value * 10) / 10
    return f"{value:.1f}"
