from django import template

register = template.Library()

@register.filter
def bytes_to_mb(value):
    if value is None:
        return 0
    return round(value / (1024*1024), 2)