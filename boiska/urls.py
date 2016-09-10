from django.conf.urls import url
from . import views

app_name = 'boiska'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^place/(?P<place_name>\w+)$', views.place, name='place'),
]
