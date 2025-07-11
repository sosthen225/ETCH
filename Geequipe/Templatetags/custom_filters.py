from django import template

register = template.Library()

@register.filter(name='index')
def index(List, i):
    try:
        return List[int(i)]
    except (IndexError, ValueError, TypeError):
        return None