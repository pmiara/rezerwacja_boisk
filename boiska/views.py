from django.shortcuts import render, get_object_or_404

from .models import Place


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
    TODO: Calendar showing availability of pitches/courts.
    """
    place_obj = get_object_or_404(Place, name=place_name)
    context = {
        'name': place_name,
        'description': place_obj.description,
        'phone_number': place_obj.phone_number,
        'city': place_obj.city,
        'street': place_obj.street,
    }
    return render(request, 'boiska/place.html', context)
