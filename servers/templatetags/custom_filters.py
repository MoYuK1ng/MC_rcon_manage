"""
Custom template filters for MC RCON Manager
"""

from django import template

register = template.Library()


@register.filter(name='replace')
def replace(value, args):
    """
    Replace occurrences of a string with another string.
    
    Usage: {{ value|replace:"old,new" }}
    Example: {{ "hello_world"|replace:"_,space" }} -> "hellospaceworld"
    """
    if not args or ',' not in args:
        return value
    
    old, new = args.split(',', 1)
    return str(value).replace(old, new)
