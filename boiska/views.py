from django.shortcuts import render, get_object_or_404, redirect
import datetime

from .models import Place, Reservation
from .forms import NewReservationForm, ManageReservationsForm, EditReservationForm
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
    place = get_object_or_404(Place, name=place_name)
    now = datetime.datetime.now()
    my_calendar = availability_calendar(place, now.year, now.month)
    context = {
        'place_name': place_name,
        'description': place.description,
        'phone_number': place.phone_number,
        'city': place.city,
        'street': place.street,
        'calendar': my_calendar,
        'year': now.year,
        'month': now.month,
    }
    return render(request, 'boiska/place.html', context)

def place_day(request, place_name, year, month, day):
    """
    Show reservations of sports grounds on a particular day.
    User can do a reservation using ReservationForm. Date and sports_ground
    fields are added automatically to the form after validation.
    """
    place = get_object_or_404(Place, name=place_name)
    sports_grounds = place.sports_grounds.all()
    context = {
        'place_name': place_name,
        'date': '/'.join((year, month, day)),
        'sports_grounds': sports_grounds,
        'result_message': None,
        'display_form': True,
    }
    if request.method == 'POST':
        new_reservation_form = NewReservationForm(data=request.POST)
        if new_reservation_form.is_valid():
            reservation = new_reservation_form.save(commit=False)
            reservation.event_date = datetime.date(int(year), int(month), int(day))
            reservation.save()
            context['display_form'] = False
            context['result_message'] = 'Twoja rezerwacja czeka na akceptację.'
        else:
            context['result_message'] = 'Twoja rezerwacja zawiera błędy.'
    else:
        new_reservation_form = NewReservationForm(place)
    context['new_reservation_form'] = new_reservation_form
    return render(request, 'boiska/place_day.html', context)

def place_admin(request, place_name):
    """
    Administrative panel for a Place administrator.
    Administrator of a Place can do following actions:
     - accept reservations
     - delete not_accepted reservations
    """
    place = get_object_or_404(Place, name=place_name)
    sports_grounds = place.sports_grounds.all()
    result_messages = []
    if request.method == 'POST':
        manage_reservations_form = ManageReservationsForm(place, data=request.POST)
        if manage_reservations_form.is_valid():
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
    manage_reservations_form = ManageReservationsForm(place)
    context = {
        'place_name': place_name,
        'reservations_not_accepted': not_accepted,
        'manage_reservations_form': manage_reservations_form,
        'result_messages': result_messages,
    }
    return render(request, 'boiska/place_admin.html', context)

def edit_reservation(request, place_name, reservation_id):
    """
    Edition of reservations for a Place administrator.
    """
    reservation = Reservation.objects.get(id=reservation_id)
    place = reservation.sports_ground.place
    edit_reservation_form = EditReservationForm(instance=reservation, place=place)
    if request.method == 'POST':
        edit_reservation_form = EditReservationForm(
            instance=reservation,
            data=request.POST,
            place=place
        )
        if edit_reservation_form.is_valid():
            edited_reservation = edit_reservation_form.save(commit=False)
            edited_reservation.save()
            return redirect('boiska:place_admin', place_name)
    context = {'edit_reservation_form': edit_reservation_form}
    return render(request, 'boiska/edit_reservation.html', context)
