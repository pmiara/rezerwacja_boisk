from django.contrib.auth.models import User

from calendar import Calendar
from random import randint
import datetime

from .models import Place, Reservation, SportsGround


def availability_calendar(place, year, month):
    """
    Availability calendar returns a list of week lists.
    Each week list contains tuples in format:
    (month_day, week_day, availability).
    Availability values:
     - 0: almost every hour is available
     - 1: a sports ground is quite busy
     - 2: very busy
    """
    my_calendar = []
    for day in Calendar().itermonthdays2(year, month):
        # create a list for a new week
        if day[1] == 0:
            my_calendar.append([])
        if day[0] == 0:
            availability = 0
        else:
            availability = check_availability(year, month, day[0], place)
        my_calendar[-1].append((
            day[0],                            # month_day
            day[1],                            # week_day
            availability
        ))
    return my_calendar


def check_availability(year, month, day, place):
    """
    Check availability of place's sports grounds on a particuar day.
    This function counts hours when sports grounds are busy - time_sum -
    and hours when sports grounds are open - total.
    Result of calculations is a value between 0 and 1, where 0 means
    there are no reservations and 1 every hour is reserved.
    Return values:
     - 0: 0.3 >= result >= 0
     - 1: 0.6 >= result > 0.3
     - 2: 1 >= result > 0.6
    """
    event_date = datetime.date(year, month, day)
    time_sum = datetime.timedelta()
    total = datetime.timedelta()
    today = datetime.date.today()
    for sports_ground in place.sports_grounds.all():
        reservations = sports_ground.reservations.filter(
            event_date=event_date,
            is_accepted=True
        )
        for reservation in reservations:
            start_time = datetime.datetime.combine(today, reservation.start_time)
            end_time = datetime.datetime.combine(today, reservation.end_time)
            time_sum += end_time - start_time
        opening_time = datetime.datetime.combine(today, sports_ground.opening_time)
        closing_time = datetime.datetime.combine(today, sports_ground.closing_time)
        total += closing_time - opening_time
    # if there are no sports grounds then time_sum / total raises exception
    if total == datetime.timedelta():
        return 0
    result = time_sum / total
    if result > 0.6:
        return 2
    elif result > 0.3:
        return 1
    else:
        return 0


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
