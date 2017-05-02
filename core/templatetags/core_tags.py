from django.template.defaulttags import register
from widget_tweaks.templatetags.widget_tweaks import set_attr


@register.filter
def placeholder(field, data):
    return set_attr(field, 'placeholder:' + data)
