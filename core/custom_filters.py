# from django import template

# register = template.Library()

# @register.filter(name='get_value')
# def get_value(dictionary, key):
#     return dictionary.get(key, False)

# @register.filter
# def get_item(dictionary, key):
#     return dictionary.get(key)


from django import template
import json

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Custom filter to get item from a dictionary"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def get_option(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def get_value(dictionary, key):
    """Custom filter to get value from a dictionary"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def json_script(value):
    """Custom filter to safely deserialize JSON data"""
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return {}