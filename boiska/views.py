from django.shortcuts import render, get_object_or_404
from calendar import Calendar
import datetime

from .models import Place
from .forms import ReservationForm

from random import randint

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
    TODO: Calendar showing availability of sports grounds.
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
    TODO: Availability values:
     - 0 -> almost every hour is available
     - 1 -> a sports ground is quite busy
     - 2 -> very busy
    """
    month_year = str(month) + '-' + str(year)
    my_calendar = []
    for day in Calendar().itermonthdays2(year, month):
        # create a list for a new week
        if day[1] == 0:
            my_calendar.append([])
        availability = check_availability(year, month, day, place_obj)
        my_calendar[-1].append((
            day[0],                            # month_day
            day[1],                            # week_day
            str(day[0]) + '-' + month_year,    # date in format d-m-yyyy
            availability
        ))
    return my_calendar

def check_availability(year, month, day, place_obj):
    """
    TODO: Check availability of place's sports grounds on a particuar day.
    """
    return randint(0,2)

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
