from django import template

register = template.Library()

@register.filter(name='get_value')
def get_value(dictionary, key):
    return dictionary.get(key, False)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)