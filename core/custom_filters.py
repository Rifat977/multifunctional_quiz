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

@register.filter
def replace_underscores_with_dropdown(question_text, dropdown_items):
    for item in dropdown_items:
        select_html = f'<select name="dropdown_{item.id}" class="form-control" style="width: auto; display: inline-block;">'
        select_html += f'<option value="">Select Answer for {item.id}</option>'
        for option in item.options.all():
            select_html += f'<option value="{option.option_text}">{option.option_text}</option>'
        select_html += '</select>'
        
        # Replace the first occurrence of '____' with the dropdown
        question_text = question_text.replace('____', select_html, 1)
    return question_text