from django import forms

from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ('email', 'surname', 'start_time', 'end_time')
