# english/templatetags/file_filters.py
import os
from django import template

register = template.Library()

@register.filter
def basename(value):
    """
    Extract the base name of a file path.
    """
    if value:
        return os.path.basename(str(value))
    return ""