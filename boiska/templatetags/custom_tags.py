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

@register.filter
def polish_month_name(month_number):
    month_names = {
        1: 'Styczeń',
        2: 'Luty',
        3: 'Marzec',
        4: 'Kwiecień',
        5: 'Maj',
        6: 'Czerwiec',
        7: 'Lipiec',
        8: 'Sierpień',
        9: 'Wrzesień',
        10: 'Październik',
        11: 'Listopad',
        12: 'Grudzień'
    }
    return month_names[month_number]
