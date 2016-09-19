from calendar import Calendar
import datetime

from .models import Place, Reservation

def availability_calendar(year, month, place_obj):
    """
    Availability calendar returns a list of week lists.
    Each week list contains tuples in format:
    (month_day, week_day, date, availability).
    Availability values:
     - 0: almost every hour is available
     - 1: a sports ground is quite busy
     - 2: very busy
    """
    month_year = str(month) + '-' + str(year)
    my_calendar = []
    for day in Calendar().itermonthdays2(year, month):
        # create a list for a new week
        if day[1] == 0:
            my_calendar.append([])
        if day[0] == 0:
            availability = 0
        else:
            availability = check_availability(year, month, day[0], place_obj)
        my_calendar[-1].append((
            day[0],                            # month_day
            day[1],                            # week_day
            str(day[0]) + '-' + month_year,    # date in format d-m-yyyy
            availability
        ))
    return my_calendar

def check_availability(year, month, day, place_obj):
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
    for sports_ground in place_obj.sports_grounds.all():
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
    result = time_sum / total
    if result > 0.6:
        return 2
    elif result > 0.3:
        return 1
    else:
        return 0

def reservation_overlap(reservation):
    event_date = reservation.event_date
    accepted_reservations = Reservation.objects.filter(
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
