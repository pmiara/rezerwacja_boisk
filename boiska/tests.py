from django.test import TestCase
from django.core.urlresolvers import resolve
from django.contrib.auth.models import User

import boiska.views as views
from .models import Place, Reservation
from .myutils import create_user, create_place, create_sports_grounds, create_reservations


class BaseViewTest:
    
    def test_url_resolves_to_correct_view(self):
        resolver_match = resolve(self.url)
        self.assertEqual(resolver_match.func, self.expected_view)
    
    def test_view_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, self.expected_template)
        self.assertEqual(response.status_code, 200)


class IndexViewTest(TestCase, BaseViewTest):
    
    def setUp(self):
        self.url = '/'
        self.expected_view = views.index
        self.expected_template = 'boiska/index.html'
    
    def test_places_in_context(self):
        response = self.client.get(self.url)
        self.assertIn('places', response.context)


class PlaceViewTest(TestCase, BaseViewTest):
    
    def setUp(self):
        place_name = 'Kórnik OSIR'
        new_place = create_place(place_name=place_name)
        self.url = '/' + place_name
        self.expected_view = views.place
        self.expected_template = 'boiska/place.html'


class PlaceAdminViewTest(TestCase, BaseViewTest):
    
    def setUp(self):
        place_name = 'Ośrodek Przywodny Rataje'
        self.place = create_place(place_name=place_name)
        self.url = '/' + place_name + '/' + 'admin'
        self.expected_view = views.place_admin
        self.expected_template = 'boiska/place_admin.html'
        self.prepare_reservations()
    
    def prepare_reservations(self):
        create_sports_grounds(self.place)
        for sports_ground in self.place.sports_grounds.all():
            create_reservations(sports_ground)
    
    def test_not_accepted_reservations_in_context(self):
        response = self.client.get(self.url)
        self.assertIn('reservations_not_accepted', response.context)
        
    def test_number_of_reservations_in_context(self):
        response = self.client.get(self.url)
        reservations_in_context = response.context['reservations_not_accepted']
        actual_reservations = Reservation.objects.filter(
            sports_ground__place = self.place
        )
        self.assertEqual(len(reservations_in_context), len(actual_reservations))
