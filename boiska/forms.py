from django import forms
from django.core.exceptions import ValidationError

from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ('email', 'surname', 'start_time', 'end_time')
        
    def is_valid(self, sports_ground):
        valid = super(ReservationForm, self).is_valid()
        if not valid:
            return valid
        start_time = self.cleaned_data['start_time']
        end_time = self.cleaned_data['end_time']
        opening_time = sports_ground.opening_time
        closing_time = sports_ground.closing_time
        if start_time > end_time or start_time < opening_time or end_time > closing_time:
            self.add_error(
                None,
                ValidationError('Nieprawidłowe godziny trwania rezerwacji.')
            )
            return False
        return True


class EditReservationsForm(forms.Form):
    action = forms.ChoiceField(
        choices=Reservation.ACTION_CHOICES,
        widget=forms.Select()
    )
    def __init__(self, place, *args, **kwargs):
        super(EditReservationsForm, self).__init__(*args, **kwargs)
        reservations = Reservation.objects.filter(
            sports_ground__place=place,
            is_accepted=False
        )
        self.fields['reservations'] = forms.ModelMultipleChoiceField(
            queryset=reservations,
            widget=forms.CheckboxSelectMultiple()
        )
