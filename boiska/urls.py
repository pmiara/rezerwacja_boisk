from django.conf.urls import url
from . import views

app_name = 'boiska'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<place_name>[\w ]+)$', views.place, name='place'),
    url(r'(?P<place_name>[\w ]+)/'
        r'(?P<my_date>\d\d?-\d\d?-\d{4})$',
        views.place_day,
        name='place_day'
    ),
]
