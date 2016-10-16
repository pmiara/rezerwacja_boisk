from django.test import TestCase
from django.core.urlresolvers import resolve
from django.contrib.auth.models import User

import datetime

import boiska.views as views
from .models import Place, Reservation
from .myutils import create_user, create_place, create_sports_grounds, create_reservations
from .forms import NewReservationForm, EditReservationForm, ManageReservationsForm


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
        sports_ground = create_sports_grounds(self.place, quantity=1)
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
        sports_grounds = create_sports_grounds(self.place)
        for sports_ground in sports_grounds:
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
        sports_ground = create_sports_grounds(self.place, quantity=1)
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


class NewReservationFormTest(TestCase):

    def setUp(self):
        place = create_place()
        self.sports_ground = create_sports_grounds(place, quantity=1)
        self.form_data = {
            'sports_ground': self.sports_ground.pk,
            'start_time': self.sports_ground.opening_time,
            'end_time': self.sports_ground.closing_time,
            'email': 'mejl@mail.com',
            'surname': 'Bananowy',
        }

    def test_correct_form_is_saved(self):
        reservation_form = NewReservationForm(data=self.form_data)
        reservation = reservation_form.save(commit=False)
        reservation.event_date = datetime.datetime.today()
        reservation.save()
        self.assertEqual(1, Reservation.objects.count())

    def test_start_time_greater_than_end_time_returns_validation_error(self):
        self.form_data['start_time'] = datetime.time(16, 50)
        self.form_data['end_time'] = datetime.time(15, 40)
        reservation_form = NewReservationForm(data=self.form_data)
        self.assertFalse(reservation_form.is_valid())

    def test_start_time_fewer_than_opening_time_returns_validation_error(self):
        opening_time = self.sports_ground.opening_time
        self.form_data['start_time'] = datetime.time(opening_time.hour - 1, 0)
        reservation_form = NewReservationForm(data=self.form_data)
        self.assertFalse(reservation_form.is_valid())

    def test_end_time_greater_than_closing_time_returns_validation_error(self):
        closing_time = self.sports_ground.closing_time
        self.form_data['end_time'] = datetime.time(closing_time.hour + 1, 0)
        reservation_form = NewReservationForm(data=self.form_data)
        self.assertFalse(reservation_form.is_valid())


class EditReservationFormTest(TestCase):

    def setUp(self):
        place = create_place()
        self.sports_ground = create_sports_grounds(place, quantity=1)
        self.reservation = create_reservations(self.sports_ground, quantity=1)
        self.form_data = {
            'sports_ground': self.sports_ground.pk,
            'start_time': self.sports_ground.opening_time,
            'end_time': self.sports_ground.closing_time,
            'is_accepted': True,
        }

    def test_correct_form_is_saved(self):
        reservation_form = EditReservationForm(
            data=self.form_data,
            instance=self.reservation
        )
        reservation_form.save()
        updated_start_time = self.form_data['start_time']
        updated_end_time = self.form_data['end_time']
        self.assertEqual(self.reservation.is_accepted, True)
        self.assertEqual(self.reservation.start_time, updated_start_time)
        self.assertEqual(self.reservation.end_time, updated_end_time)


class ManageReservationFormTest(TestCase):

    def setUp(self):
        self.place = create_place()
        self.manage_reservations_form = ManageReservationsForm(self.place)

    def test_reservations_are_added_to_fields(self):
        self.assertIn('reservations', self.manage_reservations_form.fields)

    def test_correct_reservations_are_added(self):
        correct_reservations_queryset = Reservation.objects.filter(
            sports_ground__place=self.place,
            is_accepted=False
        )
        self.assertQuerysetEqual(
            correct_reservations_queryset,
            self.manage_reservations_form.fields['reservations'].queryset
        )
