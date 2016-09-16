from django.shortcuts import render, get_object_or_404
from calendar import Calendar
import datetime

from .models import Place
from .forms import ReservationForm, EditReservationsForm

import datetime

def index(request):
    """
    Main page of the site. List of all locations.
    """
    places = Place.objects.all()
    context = {'places': places}
    return render(request, 'boiska/index.html', context)

def place(request, place_name):
    """
    Description of a place.
    Calendar showing availability of sports grounds.
    """
    place_obj = get_object_or_404(Place, name=place_name)
    now = datetime.datetime.now()
    my_calendar = availability_calendar(now.year, now.month, place_obj)
    context = {
        'name': place_name,
        'description': place_obj.description,
        'phone_number': place_obj.phone_number,
        'city': place_obj.city,
        'street': place_obj.street,
        'calendar': my_calendar,
        'year': now.year,
        'month': now.month,
    }
    return render(request, 'boiska/place.html', context)

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
            time_sum += (datetime.datetime.combine(today, reservation.end_time)
                - datetime.datetime.combine(today, reservation.start_time))
        total += (datetime.datetime.combine(today, sports_ground.closing_time)
            - datetime.datetime.combine(today, sports_ground.opening_time))
    result = time_sum / total
    if result > 0.6:
        return 2
    elif result > 0.3:
        return 1
    else:
        return 0

def place_day(request, place_name, my_date):
    """
    Show reservations of sports grounds on a particular day.
    my_date is in format: d-m-yyyy.
    """
    place_obj = get_object_or_404(Place, name=place_name)
    sports_grounds = place_obj.sports_grounds.all().order_by('local_id')
    context = {
        'name': place_name,
        'date': my_date,
        'sports_grounds': sports_grounds,
        'message': None,
        'reservation_form': None,
    }
    if request.method == 'POST':
        reservation_form = ReservationForm(data=request.POST)
        if reservation_form.is_valid():
            reservation = reservation_form.save(commit=False)
            date_strptime = datetime.datetime.strptime(
                my_date,
                "%d-%m-%Y"
            )
            date_obj = date_strptime.date()
            reservation.event_date = date_obj
            name_prefix = request.POST['name_prefix']
            local_id = request.POST['local_id']
            sports_ground = sports_grounds.get(
                name_prefix=name_prefix,
                local_id=local_id
            )
            reservation.sports_ground = sports_ground
            reservation.save()
            context['message'] = "Twoja rezerwacja czeka na akceptację."
        else:
            context['message'] = "Wystąpił błąd w procesie rezerwacji."
    else:
        reservation_form = ReservationForm()
        context['reservation_form'] = reservation_form
    return render(request, 'boiska/place_day.html', context)

def place_admin(request, place_name):
    """
    Administrative panel for a Place administrator.
    """
    place_obj = get_object_or_404(Place, name=place_name)
    sports_grounds = place_obj.sports_grounds.all()
    not_accepted = []
    for sports_ground in sports_grounds:
        for reservation in sports_ground.reservations.filter(is_accepted=False):
            not_accepted.append(reservation)
    edit_reservations_form = EditReservationsForm(place_obj)
    context = {
        'place_name': place_name,
        'reservations_not_accepted': not_accepted,
        'edit_reservations_form': edit_reservations_form,
    }
    return render(request, 'boiska/place_admin.html', context)
