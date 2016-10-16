from django.test import TestCase

import datetime

from boiska.models import Reservation
from boiska.myutils import (create_user, create_place,
    create_sports_ground, create_sports_grounds,
    create_reservation, create_reservations)
from boiska.forms import NewReservationForm, EditReservationForm, ManageReservationsForm

class NewReservationFormTest(TestCase):

    def setUp(self):
        place = create_place()
        self.sports_ground = create_sports_ground(place)
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
        self.sports_ground = create_sports_ground(place)
        self.reservation = create_reservation(self.sports_ground)
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
