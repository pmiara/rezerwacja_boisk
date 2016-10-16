from django.contrib.auth.models import User

from calendar import Calendar
from random import randint
import datetime

from .models import Place, Reservation, SportsGround


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

def create_reservation(sports_ground, date=None):
    list_of_reservations = create_reservations(
        sports_ground=sports_ground, quantity=1, date=date
    )
    return list_of_reservations[0]

def create_reservations(sports_ground, quantity=10, date=None):
    if date == None:
        now = datetime.datetime.now()
        date = now.date()
    new_reservations = []
    for _ in range(quantity):
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

        new_reservations.append(
            sports_ground.reservations.create(
                surname='Surname',
                email='mail@site.com',
                event_date=date,
                start_time=start_time,
                end_time=end_time,
                is_accepted=False
            )
        )
    return new_reservations

def create_sports_ground(place):
    list_of_sports_grounds = create_sports_grounds(place=place, quantity=1)
    return list_of_sports_grounds[0]

def create_sports_grounds(place, quantity=3):
    new_sports_grounds = []
    for _ in range(quantity):
        new_sports_grounds.append(
            place.sports_grounds.create(
                opening_time=datetime.time(8),
                closing_time=datetime.time(20)
            )
        )
    return new_sports_grounds
