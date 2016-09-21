from django import forms
from django.core.exceptions import ValidationError

from .models import Reservation, SportsGround

class ReservationForm(forms.ModelForm):
    def __init__(self, place=None, *args, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)
        if place is not None:
            self.fields['sports_ground'].queryset = SportsGround.objects.filter(place=place)
    
    class Meta:
        model = Reservation
        fields = ('sports_ground', 'email', 'surname', 'start_time', 'end_time')
        
    def clean(self):
        start_time = self.cleaned_data['start_time']
        end_time = self.cleaned_data['end_time']
        sports_ground = self.cleaned_data['sports_ground']
        opening_time = sports_ground.opening_time
        closing_time = sports_ground.closing_time
        if start_time > end_time or start_time < opening_time or end_time > closing_time:
            raise ValidationError('Nieprawidłowe godziny trwania rezerwacji.')
        return self.cleaned_data


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


class EditSingleReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = '__all__'
