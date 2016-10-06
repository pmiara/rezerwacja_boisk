from django.test import TestCase
from django.core.urlresolvers import resolve
from django.contrib.auth.models import User

import boiska.views as views
from .models import Place


def create_user(username='ExampleMan', password='qwerty123'):
    return User.objects.create(username=username, password=password)


def create_place(place_name='Poznań Rataje', place_administrator=None):
    if place_administrator == None:
        place_administrator = create_user()
    place_args = {
        'name': place_name,
        'administrator': place_administrator,
        'description': 'Example description.',
        'phone_number': '123321123',
        'city': 'Poznań',
        'street': 'Nowina',
    }
    return Place.objects.create(**place_args)


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
