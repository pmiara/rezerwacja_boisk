from django import forms
from django.core.exceptions import ValidationError

from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ('email', 'surname', 'start_time', 'end_time')

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
