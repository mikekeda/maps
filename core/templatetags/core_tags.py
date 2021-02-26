from django.template.defaulttags import register
from widget_tweaks.templatetags.widget_tweaks import set_attr


@register.filter
def placeholder(field, data):
    return set_attr(field, "placeholder:" + data)


@register.simple_tag
def update_param(request, param, value=None):
    params = request.GET.copy()
    if value:
        params[param] = value
    else:
        params.pop(param, None)

    path = request.path
    if params:
        path += "?" + params.urlencode()

    return path
