import datetime
from django import template
register = template.Library()

@register.filter
def sort_by(query_set, order):
    return query_set.order_by(order)

@register.filter
def filter_day(query_set, my_date):
    date_obj = datetime.datetime.strptime(my_date, "%Y/%m/%d").date()
    return query_set.filter(event_date=date_obj)
