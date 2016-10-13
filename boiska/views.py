from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import Http404

import datetime
from calendar import Calendar

from .models import Place, Reservation
from .forms import (NewReservationForm, ManageReservationsForm,
    EditReservationForm, EditPlaceForm)
from .myutils import reservation_overlap


class IndexView(View):
    """
    Main page of the site. List of all locations.
    """
    def get(self, request):
        places = Place.objects.all()
        context = {'places': places}
        return render(request, 'boiska/index.html', context)


class PlaceView(View):
    """
    Description of a place.
    Calendar showing availability of sports grounds.
    """

    EMPTY = 0
    BUSY = 1
    VERY_BUSY = 2

    def get(self, request, place_name, year=None, month=None):
        self.place = get_object_or_404(Place, name=place_name)
        self.year = year
        self.month = month
        self.prepare_and_check_year_month()
        my_calendar = self.availability_calendar()
        context = {
            'place': self.place,
            'calendar': my_calendar,
            'year': self.year,
            'month': self.month,
        }
        return render(request, 'boiska/place.html', context)

    def prepare_and_check_year_month(self):
        now = datetime.datetime.now()
        if self.year == None:
            self.year = now.year
        else:
            self.year = int(self.year)
        if self.month == None:
            self.month = now.month
        else:
            self.month = int(self.month)
        if self.month < 1 or self.month > 12:
            raise Http404

    def availability_calendar(self):
        """
        Availability calendar returns a list of week lists.
        """
        my_calendar = []
        for day in Calendar().itermonthdays2(self.year, self.month):
            day_dict = {
                'month_day': day[0],
                'week_day': day[1],
                'availability': None,
            }
            if day_dict['week_day'] == 0:
                my_calendar.append([])
            if day_dict['month_day'] != 0:
                day_dict['availability'] = self.check_availability(day_dict['month_day'])
            my_calendar[-1].append(day_dict)
        return my_calendar

    def check_availability(self, month_day):
        """
        Check availability of place's sports grounds on a particuar day.
        """
        event_date = datetime.date(self.year, self.month, month_day)
        time_sum = datetime.timedelta()
        total = datetime.timedelta()
        today = datetime.date.today()

        for sports_ground in self.place.sports_grounds.all():
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

        if total == datetime.timedelta():
            return self.EMPTY
        result = time_sum / total
        if result > 0.6:
            return self.VERY_BUSY
        elif result > 0.3:
            return self.BUSY
        else:
            return self.EMPTY


class PlaceDayView(View):
    """
    Show reservations of sports grounds on a particular day.
    User can do a reservation using ReservationForm. Date and sports_ground
    fields are added automatically to the form after validation.
    """
    def get(self, request, place_name, year, month, day):
        self.initial_settings(place_name, year, month, day)
        new_reservation_form = NewReservationForm(self.place)
        self.context['new_reservation_form'] = new_reservation_form
        return render(request, 'boiska/place_day.html', self.context)

    def post(self, request, place_name, year, month, day):
        self.initial_settings(place_name, year, month, day)
        self.context['result_message'] = None
        new_reservation_form = NewReservationForm(data=request.POST)
        if new_reservation_form.is_valid():
            reservation = new_reservation_form.save(commit=False)
            reservation.event_date = datetime.date(int(year), int(month), int(day))
            reservation.save()
            self.context['result_message'] = 'Twoja rezerwacja czeka na akceptację.'
        else:
            self.context['result_message'] = 'Twoja rezerwacja zawiera błędy.'
        self.context['new_reservation_form'] = new_reservation_form
        return render(request, 'boiska/place_day.html', self.context)

    def initial_settings(self, place_name, year, month, day):
        self.place_name = place_name
        self.year = year
        self.month = month
        self.day = day
        self.place = get_object_or_404(Place, name=self.place_name)
        self.sports_grounds = self.place.sports_grounds.all()
        self.prepare_context()

    def prepare_context(self):
        self.context = {
            'place_name': self.place_name,
            'date': '/'.join((self.year, self.month, self.day)),
            'sports_grounds': self.sports_grounds,
        }


def place_admin(request, place_name):
    """
    Administrative panel for a Place administrator.
    Administrator of a Place can do following actions:
     - accept reservations
     - delete not_accepted reservations
     - edit reservations
    """
    place = get_object_or_404(Place, name=place_name)
    sports_grounds = place.sports_grounds.all()
    result_messages = []
    if request.method == 'POST':
        manage_reservations_form = ManageReservationsForm(
            place,
            data=request.POST
        )
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
        'place': place,
        'sports_grounds': sports_grounds,
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
    edit_reservation_form = EditReservationForm(
        instance=reservation,
        place=place
    )
    if request.method == 'POST':
        edit_reservation_form = EditReservationForm(
            instance=reservation,
            data=request.POST,
            place=place
        )
        if edit_reservation_form.is_valid():
            edit_reservation_form.save()
            return redirect('boiska:place_admin', place_name)
    context = {
        'edit_reservation_form': edit_reservation_form,
        'place_name': place_name,
        'reservation': reservation,
    }
    return render(request, 'boiska/edit_reservation.html', context)

def edit_place(request, place_name):
    """
    Edition of place.
    """
    place = Place.objects.get(name=place_name)
    edit_place_form = EditPlaceForm(instance=place)
    if request.method == 'POST':
        edit_place_form = EditPlaceForm(instance=place, data=request.POST)
        if edit_place_form.is_valid():
            edit_place_form.save()
            return redirect('boiska:place_admin', place_name)
    context = {
        'edit_place_form': edit_place_form,
        'place_name': place_name,
    }
    return render(request, 'boiska/edit_place.html', context)
