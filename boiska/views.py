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
    }
    return render(request, 'boiska/place.html', context)

def availability_calendar(year, month, place_obj):
    """
    Availability calendar returns a list of week lists.
    Each week list contains tuples in format:
    (month_day, week_day, availability).
    TODO: Availability values:
     - 0 -> almost every hour is available
     - 1 -> a sports ground is quite busy
     - 2 -> very busy
    """
    result = []
    my_calendar = Calendar()
    for day in my_calendar.itermonthdays2(year, month):
        # create a list for a new week
        if day[1] == 0:
            result.append([])
        availability = check_availability(year, month, day, place_obj)
        result[-1].append((day[0], day[1], availability))
    return result

def check_availability(year, month, day, place_obj):
    """
    TODO: Check availability of place's sports grounds on a particuar day.
    """
    return randint(0,2)
