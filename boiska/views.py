from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.views import View
from django.http import Http404

import datetime
from calendar import Calendar

from .models import Place, Reservation
from .forms import (NewReservationForm, ManageReservationsForm,
    EditReservationForm, EditPlaceForm)


class IndexView(ListView):
    """
    Main page of the site. List of all locations.
    """
    model = Place
    template_name = 'boiska/index.html'


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
        self.prepare_context()
        if not self.is_date_valid():
            raise Http404
        new_reservation_form = NewReservationForm(self.place)
        self.context['new_reservation_form'] = new_reservation_form
        return render(request, 'boiska/place_day.html', self.context)

    def post(self, request, place_name, year, month, day):
        self.initial_settings(place_name, year, month, day)
        self.prepare_context()
        if not self.is_date_valid():
            raise Http404
        self.context['result_message'] = None
        new_reservation_form = NewReservationForm(data=request.POST)
        if new_reservation_form.is_valid():
            reservation = new_reservation_form.save(commit=False)
            reservation.event_date = datetime.date(self.year, self.month, self.day)
            reservation.save()
            self.context['result_message'] = 'Twoja rezerwacja czeka na akceptację.'
        else:
            self.context['result_message'] = 'Twoja rezerwacja zawiera błędy.'
        self.context['new_reservation_form'] = new_reservation_form
        return render(request, 'boiska/place_day.html', self.context)

    def initial_settings(self, place_name, year, month, day):
        self.place_name = place_name
        self.year = int(year)
        self.month = int(month)
        self.day = int(day)
        self.place = get_object_or_404(Place, name=self.place_name)
        self.sports_grounds = self.place.sports_grounds.all()

    def prepare_context(self):
        self.context = {
            'place_name': self.place_name,
            'date': str(self.year) + '/' + str(self.month) + '/' + str(self.day),
            'sports_grounds': self.sports_grounds,
            'new_reservation_form': None,
            'result_message': None,
        }

    def is_date_valid(self):
        try:
            datetime.date(self.year, self.month, self.day)
            return True
        except:
            return False


class PlaceAdminView(View):
    """
    Administrative panel for a Place administrator.
    """

    def get(self, request, place_name):
        self.initial_settings(place_name)
        self.prepare_context()
        self.prepare_reservations_not_accepted()
        manage_reservations_form = ManageReservationsForm(self.place)
        self.context['manage_reservations_form'] = manage_reservations_form
        return render(request, 'boiska/place_admin.html', self.context)

    def post(self, request, place_name):
        self.initial_settings(place_name)
        self.prepare_context()
        self.prepare_reservations_not_accepted()
        manage_reservations_form = ManageReservationsForm(
            self.place,
            data=request.POST
        )
        if manage_reservations_form.is_valid():
            reservations_ids = request.POST.getlist('reservations')
            reservations = Reservation.objects.filter(
                sports_ground__in=self.sports_grounds,
                id__in=reservations_ids
            )
            action = int(request.POST['action'])
            self.apply_action_to_selected_reservations(reservations, action)
        return render(request, 'boiska/place_admin.html', self.context)

    def initial_settings(self, place_name):
        self.place = get_object_or_404(Place, name=place_name)
        self.sports_grounds = self.place.sports_grounds.all()

    def prepare_context(self):
        self.context = {
            'place': self.place,
            'sports_grounds': self.sports_grounds,
            'reservations_not_accepted': None,
            'manage_reservations_form': None,
            'result_messages': None,
        }

    def prepare_reservations_not_accepted(self):
        reservations_not_accepted = []
        for sports_ground in self.sports_grounds:
            for reservation in sports_ground.reservations.filter(is_accepted=False):
                reservations_not_accepted.append(reservation)
        self.context['reservations_not_accepted'] = reservations_not_accepted

    def apply_action_to_selected_reservations(self, reservations, action):
        result_messages = []
        for reservation in reservations:
            if action == Reservation.ACCEPT:
                overlap = self.reservation_overlap(reservation)
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
        self.context['result_messages'] = result_messages

    def reservation_overlap(self, reservation):
        """
        Check if a reservation can be accepted. If addition of a new reservation
        causes an overlap, it can't be aaccepted.
        """
        event_date = reservation.event_date
        accepted_reservations = Reservation.objects.filter(
            sports_ground=reservation.sports_ground,
            event_date=event_date,
            is_accepted=True
        )
        lower_bound_a = reservation.start_time
        upper_bound_a = reservation.end_time
        for accepted_reservation in accepted_reservations:
            lower_bound_b = accepted_reservation.start_time
            upper_bound_b = accepted_reservation.end_time
            if lower_bound_a < upper_bound_b and lower_bound_b < upper_bound_a:
                return True
        return False


class EditReservationView(View):
    """
    Edition of reservations for a Place administrator.
    """

    def get(self, request, place_name, reservation_id):
        self.initial_settings(place_name, reservation_id)
        self.edit_reservation_form = EditReservationForm(
            instance=self.reservation,
            place=self.place
        )
        self.prepare_context()
        return render(request, 'boiska/edit_reservation.html', self.context)

    def post(self, request, place_name, reservation_id):
        self.initial_settings(place_name, reservation_id)
        self.edit_reservation_form = EditReservationForm(
            instance=self.reservation,
            place=self.place,
            data=request.POST
        )
        self.prepare_context()
        if self.edit_reservation_form.is_valid():
            self.edit_reservation_form.save()
            return redirect('boiska:place_admin', place_name)
        return render(request, 'boiska/edit_reservation.html', self.context)

    def initial_settings(self, place_name, reservation_id):
        self.reservation = Reservation.objects.get(id=reservation_id)
        self.place = self.reservation.sports_ground.place
        self.place_name = place_name

    def prepare_context(self):
        self.context = {
            'edit_reservation_form': self.edit_reservation_form,
            'place_name': self.place_name,
            'reservation': self.reservation,
        }


class EditPlaceView(View):

    def get(self, request, place_name):
        place = Place.objects.get(name=place_name)
        edit_place_form = EditPlaceForm(instance=place)
        context = {
            'edit_place_form': edit_place_form,
            'place_name': place_name,
        }
        return render(request, 'boiska/edit_place.html', context)

    def post(self, request, place_name):
        place = Place.objects.get(name=place_name)
        edit_place_form = EditPlaceForm(instance=place, data=request.POST)
        if edit_place_form.is_valid():
            edit_place_form.save()
            return redirect('boiska:place_admin', place_name)
        context = {
            'edit_place_form': edit_place_form,
            'place_name': place_name,
        }
        return render(request, 'boiska/edit_place.html', context)
