from django.shortcuts import render, get_object_or_404
import datetime

from .models import Place, Reservation
from .forms import ReservationForm, EditReservationsForm, EditSingleReservationForm
from .myutils import availability_calendar, check_availability, reservation_overlap 


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

def place_day(request, place_name, my_date):
    """
    Show reservations of sports grounds on a particular day.
    my_date is in format: d-m-yyyy.
    User can do a reservation using ReservationForm. Date and sports_ground
    fields are added automatically to the form after validation.
    """
    place_obj = get_object_or_404(Place, name=place_name)
    sports_grounds = place_obj.sports_grounds.all()
    context = {
        'name': place_name,
        'date': my_date,
        'sports_grounds': sports_grounds,
        'result_message': None,
        'reservation_form': None,
        'display_form': True,
    }
    if request.method == 'POST':
        date_strptime = datetime.datetime.strptime(my_date, "%d-%m-%Y")
        date_obj = date_strptime.date()
        name_prefix = request.POST['name_prefix']
        local_id = request.POST['local_id']
        sports_ground = sports_grounds.get(
            name_prefix=name_prefix,
            local_id=local_id
        )
        reservation_form = ReservationForm(data=request.POST)
        if reservation_form.is_valid(sports_ground):
            reservation = reservation_form.save(commit=False)
            reservation.sports_ground = sports_ground
            reservation.event_date = date_obj
            reservation.save()
            context['display_form'] = False
            context['result_message'] = 'Twoja rezerwacja czeka na akceptację.'
        else:
            context['result_message'] = 'Twoja rezerwacja zawiera błędy.'
    else:
        reservation_form = ReservationForm()
    context['reservation_form'] = reservation_form
    return render(request, 'boiska/place_day.html', context)

def place_admin(request, place_name):
    """
    Administrative panel for a Place administrator.
    Administrator of a Place can do following actions:
     - accept reservations
     - delete not_accepted reservations
    """
    place_obj = get_object_or_404(Place, name=place_name)
    sports_grounds = place_obj.sports_grounds.all()
    result_messages = []
    if request.method == 'POST':
        edit_reservations_form = EditReservationsForm(place_obj, data=request.POST)
        if edit_reservations_form.is_valid():
            reservations_ids = request.POST.getlist('reservations')
            reservations = Reservation.objects.filter(
                sports_ground__in=sports_grounds,
                id__in=reservations_ids
            )
            action = int(request.POST['action'])
            for reservation in reservations:
                if action == Reservation.ACCEPT:
                    overlap = reservation_overlap(reservation)
                    if overlap == False:
                        reservation.is_accepted = True
                        reservation.save()
                        result_messages.append(
                            'Zaakceptowano: ' + str(reservation)
                        )
                    else:
                        result_messages.append(
                            'Rezerwacja nachodzi na inną: ' + str(reservation)
                        )
                elif action == Reservation.DELETE:
                    reservation.delete()
                    result_messages.append('Usunięto: ' + str(reservation))
    not_accepted = []
    for sports_ground in sports_grounds:
        for reservation in sports_ground.reservations.filter(is_accepted=False):
            not_accepted.append(reservation)
    edit_reservations_form = EditReservationsForm(place_obj)
    context = {
        'place_name': place_name,
        'reservations_not_accepted': not_accepted,
        'edit_reservations_form': edit_reservations_form,
        'result_messages': result_messages,
    }
    return render(request, 'boiska/place_admin.html', context)

def edit_reservation(request, place_name, reservation_id):
    """
    Edition of reservations for a Place administrator.
    """
    reservation = Reservation.objects.get(id=reservation_id)
    edit_single_reservation_form = EditSingleReservationForm()
    context = {
        'reservation': reservation,
        'edit_single_reservation_form': edit_single_reservation_form,
    }
    return render(request, 'boiska/edit_reservation.html', context)
