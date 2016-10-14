from django.test import TestCase
from django.core.urlresolvers import resolve
from django.contrib.auth.models import User

import datetime

import boiska.views as views
from .models import Place, Reservation
from .myutils import create_user, create_place, create_sports_grounds, create_reservations
from .forms import NewReservationForm


class BasicViewTest:

    def test_url_resolves_to_correct_view(self):
        resolver_match = resolve(self.url)
        self.assertEqual(resolver_match.view_name, self.expected_view_name)

    def test_view_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, self.expected_template)
        self.assertEqual(response.status_code, 200)

    def test_template_extends_after_base(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'boiska/base.html')


class IndexViewTest(TestCase, BasicViewTest):

    def setUp(self):
        self.url = '/'
        self.expected_view_name = 'boiska:index'
        self.expected_template = 'boiska/index.html'

    def test_places_in_context(self):
        response = self.client.get(self.url)
        self.assertIn('place_list', response.context)


class PlaceViewTest(TestCase, BasicViewTest):

    def setUp(self):
        self.place_name = 'Kórnik OSIR'
        self.place = create_place(place_name=self.place_name)
        self.EMPTY = views.PlaceView.EMPTY
        self.BUSY = views.PlaceView.BUSY
        self.VERY_BUSY = views.PlaceView.VERY_BUSY
        self.url = '/' + self.place_name
        self.expected_view_name = 'boiska:place'
        self.expected_template = 'boiska/place.html'

    def test_year_and_month_in_context(self):
        response = self.client.get(self.url)
        self.assertIn('year', response.context)
        self.assertIn('month', response.context)

    def test_place_in_context(self):
        response = self.client.get(self.url)
        self.assertIn('place', response.context)

    def test_calendar_in_context(self):
        response = self.client.get(self.url)
        self.assertIn('calendar', response.context)

    def test_default_year_and_month(self):
        response = self.client.get(self.url)
        today = datetime.datetime.today()
        expected_year = today.year
        expected_month = today.month
        self.assertEqual(response.context['year'], expected_year)
        self.assertEqual(response.context['month'], expected_month)

    def test_incorrect_month_in_url_raises_404(self):
        url_with_incorrect_month = self.url + '/2016/13'
        response = self.client.get(url_with_incorrect_month)
        self.assertEqual(response.status_code, 404)

    def test_calendar_has_days_with_availability(self):
        response = self.client.get(self.url)
        calendar = response.context['calendar']
        for week in calendar:
            for day in week:
                if day['month_day'] == 0:
                    self.assertEqual(day['availability'], None)
                else:
                    self.assertIn(
                        day['availability'],
                        [self.EMPTY, self.BUSY, self.VERY_BUSY]
                    )

    def test_availability_when_there_are_no_reservations(self):
        response = self.client.get(self.url)
        calendar = response.context['calendar']
        for week in calendar:
            for day in week:
                if day['month_day'] == 0:
                    self.assertEqual(day['availability'], None)
                else:
                    self.assertEqual(day['availability'], self.EMPTY)

    def test_availability_when_every_hour_is_busy(self):
        create_sports_grounds(self.place, quantity=1)
        sports_ground = self.place.sports_grounds.get()
        today = datetime.datetime.today()
        sports_ground.reservations.create(
            start_time = sports_ground.opening_time,
            end_time = sports_ground.closing_time,
            event_date = today,
            email = 'poprawny@strona.pl',
            surname = 'Testowy',
            is_accepted = True,
        )
        response = self.client.get(self.url)
        calendar = response.context['calendar']
        for week in calendar:
            for day in week:
                if day['month_day'] == today.day:
                    self.assertEqual(day['availability'], self.VERY_BUSY)


class PlaceAdminViewTest(TestCase, BasicViewTest):

    def setUp(self):
        place_name = 'Ośrodek Przywodny Rataje'
        self.place = create_place(place_name=place_name)
        self.url = '/' + place_name + '/' + 'admin'
        self.expected_view_name = 'boiska:place_admin'
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


class PlaceDayViewTest(TestCase, BasicViewTest):

    def setUp(self):
        self.place_name = 'Wejcherowo'
        self.place = create_place(place_name=self.place_name)
        self.url = '/' + self.place_name + '/2016/09/23'
        self.expected_view_name = 'boiska:place_day'
        self.expected_template = 'boiska/place_day.html'

    def test_place_name_in_context(self):
        response = self.client.get(self.url)
        self.assertIn('place_name', response.context)

    def test_date_in_context(self):
        response = self.client.get(self.url)
        self.assertIn('date', response.context)

    def test_sports_grounds_in_context(self):
        response = self.client.get(self.url)
        self.assertIn('sports_grounds', response.context)

    def test_new_reservation_form_in_context(self):
        response = self.client.get(self.url)
        self.assertIn('new_reservation_form', response.context)

    def test_incorrect_date_in_url_raises_404(self):
        url_with_incorrect_date = '/' + self.place_name + '/2016/02/31'
        response = self.client.get(url_with_incorrect_date)
        self.assertEqual(response.status_code, 404)

    def test_event_date_is_added_to_saved_form(self):
        create_sports_grounds(self.place, quantity=1)
        sports_ground = self.place.sports_grounds.get()
        form_data = {
            'sports_ground': sports_ground.pk,
            'start_time': sports_ground.opening_time,
            'end_time': sports_ground.closing_time,
            'email': 'mejl@mail.com',
            'surname': 'Bananowy',
        }
        response = self.client.post(self.url, form_data)
        new_reservation = sports_ground.reservations.get()
        self.assertTrue(hasattr(new_reservation, 'event_date'))
