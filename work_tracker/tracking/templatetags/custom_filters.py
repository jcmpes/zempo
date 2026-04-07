# tracking/templatetags/custom_filters.py
from django import template
import datetime

register = template.Library()

@register.filter
def format_time(seconds):
    """
    Convierte segundos en una cadena con formato HH:MM:SS.
    """
    if seconds is None:
        return "00:00:00"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    # seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}"
