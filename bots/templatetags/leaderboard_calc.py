from django import template

from millify import millify

register = template.Library()

@register.filter
def rank(counter, page):
    return counter + (page - 1) * 100

@register.filter
def millify_val(value):
    return millify(value, precision=1)
