from django import template

register = template.Library()


@register.filter(name='range')
def filter_range(end, start):
    return range(start, end)

@register.filter(name='module')
def filter_module(arg, value):
    return arg % value

@register.filter(name='less')
def filter_less(arg, value):
    return (arg-value)
