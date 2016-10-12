from django.contrib.auth.models import User

from calendar import Calendar
from random import randint
import datetime

from .models import Place, Reservation, SportsGround


def reservation_overlap(reservation):
    """
    Check if a reservation can be accepted. If addition of a new reservation
    causes an overlap, it can't be aaccepted.
    Return values:
     - True: there is an overlap
     - False: there isn't
    """
    event_date = reservation.event_date
    accepted_reservations = Reservation.objects.filter(
        sports_ground=reservation.sports_ground,
        event_date=event_date,
        is_accepted=True
    )
    for accepted_reservation in accepted_reservations:
        start_a = accepted_reservation.start_time
        end_a = accepted_reservation.end_time
        start_b = reservation.start_time
        end_b = reservation.end_time
        if start_a < end_b and start_b < end_a:
            return True
    return False


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


def create_reservations(sports_ground, number_of_reservations=10, date=None):
    if date == None:
        now = datetime.datetime.now()
        date = now.date()
    for _ in range(number_of_reservations):
        start_time = datetime.datetime.combine(
            datetime.datetime.now(),
            sports_ground.opening_time
        )
        hours_from_start = datetime.timedelta(hours=randint(1, 5))
        start_time += hours_from_start

        end_time = datetime.datetime.combine(
            datetime.datetime.now(),
            sports_ground.closing_time
        )
        duration = datetime.timedelta(hours=randint(1, 3))
        end_time += duration

        sports_ground.reservations.create(
            surname='Surname',
            email='mail@site.com',
            event_date=date,
            start_time=start_time,
            end_time=end_time,
            is_accepted=False
        )


def create_sports_grounds(place, number_of_sports_grounds=3):
    for _ in range(number_of_sports_grounds):
        place.sports_grounds.create(
            opening_time=datetime.time(8),
            closing_time=datetime.time(20)
        )
