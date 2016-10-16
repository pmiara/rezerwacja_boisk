from django.conf.urls import url
from . import views

app_name = 'boiska'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(),
        name='index'
    ),
    url(r'^(?P<place_name>[\w ]+)$',
        views.PlaceView.as_view(),
        name='place'
    ),
    url(r'^(?P<place_name>[\w ]+)/'
        r'(?P<year>\d{4})/'
        r'(?P<month>\d\d?)$',
        views.PlaceView.as_view(),
        name='place'
    ),
    url(r'(?P<place_name>[\w ]+)/'
        r'(?P<year>\d{4})/'
        r'(?P<month>\d\d?)/'
        r'(?P<day>\d\d?)$',
        views.PlaceDayView.as_view(),
        name='place_day'
    ),
    url(r'(?P<place_name>[\w ]+)/'
        r'admin$',
        views.PlaceAdminView.as_view(),
        name='place_admin'
    ),
    url(r'(?P<place_name>[\w ]+)/'
        r'admin/edit_reservation/'
        r'(?P<reservation_id>\d+)$',
        views.EditReservationView.as_view(),
        name='edit_reservation'
    ),
    url(r'(?P<place_name>[\w ]+)/'
        r'admin/edit_place$',
        views.EditPlaceView.as_view(),
        name='edit_place'
    ),
]
