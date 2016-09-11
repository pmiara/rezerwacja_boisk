from django.shortcuts import render, get_object_or_404
from calendar import Calendar
from datetime import datetime

from .models import Place

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
    now = datetime.now()
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

def place_day(request, place_name, date):
    """
    Show reservations of sports grounds on a particular day.
    Date is in format: d-m-yyyy.
    """
    day, month, year = date.split('-')
    place_obj = get_object_or_404(Place, name=place_name)
    context = {
        'name': place_name,
        'date': date,
    }
    return render(request, 'boiska/place_day.html', context)
    
