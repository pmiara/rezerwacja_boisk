from django import template
register = template.Library()

@register.filter
def sort_by(query_set, order):
    return query_set.order_by(order)
