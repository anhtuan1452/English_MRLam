# DocumentManagement/templatetags/document_filters.py
from django import template

register = template.Library()

@register.filter
def split(value, key):
    """
    Returns the value split by key.
    """
    return value.split(key)