# do_reservations.py
# Create some fake reservations

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
import django
django.setup()

from boiska.models import Reservation, SportsGround
import datetime
import random

START_DATE = datetime.date(2016,9,1) # <----------
END_DATE = datetime.date(2016,9,5)   # <----------

SURNAMES = [
    'Nowak', 'Kowalski', 'Wiśniewski', 'Wójcik', 'Kowalczyk',
    'Kamiński', 'Lewandowski', 'Dąbrowski', 'Zieliński', 'Szymański',
    'Woźniak', 'Kozłowski', 'Jankowski', 'Mazur', 'Wojciechowski',
    'Kwiatkowski', 'Krawczyk', 'Kaczmarek', 'Piotrowski', 'Grabowski',
    'Zając', 'Pawłowski', 'Michalski', 'Król', 'Nowakowski',
    'Wieczorek', 'Wróbel', 'Jabłoński', 'Dudek', 'Adamczyk', 'Majewski',
    'Nowicki', 'Olszewski', 'Stępień', 'Jaworski', 'Malinowski',
    'Pawlak', 'Górski', 'Witkowski', 'Walczak', 'Sikora', 'Rutkowski',
    'Baran', 'Michalak', 'Szewczyk', 'Ostrowski', 'Tomaszewski',
    'Pietrzak', 'Duda', 'Zalewski', 'Wróblewski', 'Jasiński',
    'Marciniak', 'Bąk', 'Zawadzki', 'Sadowski', 'Jakubowski', 'Wilk',
    'Włodarczyk', 'Chmielewski', 'Borkowski', 'Sokołowski',
    'Szczepański', 'Sawicki', 'Lis', 'Kucharski', 'Mazurek',
    'Kubiak', 'Kalinowski', 'Wysocki', 'Maciejewski', 'Czarnecki',
    'Kołodziej', 'Urbański', 'Kaźmierczak', 'Sobczak', 'Konieczny',
    'Głowacki', 'Zakrzewski', 'Krupa', 'Wasilewski', 'Krajewski',
    'Adamski', 'Sikorski', 'Mróz', 'Laskowski', 'Gajewski',
    'Ziółkowski', 'Szulc', 'Makowski', 'Czerwiński', 'Baranowski',
    'Szymczak', 'Brzeziński', 'Kaczmarczyk', 'Przybylski', 'Cieślak',
    'Borowski', 'Błaszczyk', 'Andrzejewski',
]

MAIL_NAMES = [
    'dyzio', 'pogromca222', 'ziutek0', 'buziaczek', 'rycerz666', 'ahoj',
    '1typowy1', 'kotlet14', 'your.boss', 'super.player', 'thebest1',
    'professional', 'porkchop', 'pierogi', 'exterminator45', 'kuba92',
    'pioter22', 'madzia96', 'informatyk7', 'h3ll0', 'andrzej85',
    'grzes1', 'karol411', 'jp2', 'reeeemonty', 'dzikie_wieprze', 'winatuska',
    'orgazmator', 'tobylzamach', 'korwinkrol', 'grazyna', 'janusz74',
    'bozena52',
]

MAIL_DOMAINS = [
    'buziaczek.pl', 'gmail.com', 'hotmail.com', 'example.com',
    'site.com', 'onet.pl', 'interia.pl', 'wp.pl', 'op.pl', 'ba.com',
]

ONE_DAY = datetime.timedelta(days=1)
ONE_HOUR = datetime.timedelta(hours=1)
HALF_HOUR = datetime.timedelta(minutes=30)

def main():
    sports_grounds = SportsGround.objects.all()
    for sports_ground in sports_grounds:
        current_day = START_DATE
        # time objects have to be converted to datetime object so that
        # we can add timedeltas to them
        opening_time = sports_ground.opening_time
        opening_time = datetime.datetime.combine(
            datetime.datetime.now(),
            opening_time
        )
        closing_time = sports_ground.closing_time
        closing_time = datetime.datetime.combine(
            datetime.datetime.now(),
            closing_time
        )
        while current_day <= END_DATE:
            current_time = opening_time
            while current_time <= closing_time - ONE_HOUR:
                reservation_time = choose_duration(current_time)
                if reservation_time == None:
                    current_time += ONE_HOUR
                else:
                    if current_time + reservation_time > closing_time:
                        reservation_time = closing_time - current_time
                    do_reservation(
                        current_day,
                        current_time,
                        reservation_time,
                        sports_ground
                    )
                    current_time += reservation_time
            current_day += ONE_DAY

def choose_duration(start_time):
    # the later the bigger chance for success
    if random.random() > start_time.hour / 24:
        return None
    reservation_time = datetime.timedelta(hours=1)
    if random.random() < 0.50:
        reservation_time += ONE_HOUR
    if random.random() < 0.50:
        reservation_time += HALF_HOUR
    return reservation_time

def do_reservation(event_date, start_time, duration, sports_ground):
    surname = random.choice(SURNAMES)
    mail_address = (random.choice(MAIL_NAMES) + '@' + random.choice(MAIL_DOMAINS))
    end_time = start_time + duration
    context = {
        'surname': surname,
        'email': mail_address,
        'event_date': event_date,
        'start_time': start_time,
        'end_time': end_time,
        'sports_ground': sports_ground,
        'is_accepted': True,
    }
    reservation = Reservation.objects.create(**context)
    reservation.save()

if __name__ == '__main__':
    main()
