from django.contrib.auth.models import User
from django.db import models


class Place(models.Model):
    """
    Place is a location with sports grounds. Administrator is a person
    who can edit info about a Place and manage registrations.
    """
    name = models.CharField(max_length=40, primary_key=True)
    administrator = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    description = models.CharField(max_length=500)
    phone_number = models.CharField(max_length=20, default=None)
    city = models.CharField(max_length=30)
    street = models.CharField(max_length=50)
    def __str__(self):
        return self.name


class SportsGround(models.Model):
    """
    SportsGround is a pitch/court which belongs to a Place and can have
    reservations attached to it.
    SportsGround can be closed for some time, for example during
    the winter.
    """
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name='sports_grounds'
    )
    name_prefix = models.CharField(
        max_length=30,
        default='Boisko nr',
        blank=True
    )
    local_id = models.PositiveIntegerField(blank=True, default=None)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    start_season_date = models.DateField(
        blank=True,
        null=True,
        default=None
    )
    end_season_date = models.DateField(
        blank=True,
        null=True,
        default=None
    )
    
    class Meta:
        unique_together = ('place', 'name_prefix', 'local_id')
    
    def local_name(self):
        return self.name_prefix + ' ' + str(self.local_id)
    
    def __str__(self):
        result = self.name_prefix + ' '
        result += str(self.local_id) + ', ' + self.place.name
        return result
    
    def save(self, *args, **kwargs):
        if self.local_id is None:
            self.local_id = get_local_id(self.place, self.name_prefix)
        super(SportsGround, self).save(*args, **kwargs)


def get_local_id(place, name_prefix):
    """
    This function is used when a SportsGround instance is being saved.
    """
    sports_grounds = place.sports_grounds.filter(
        name_prefix=name_prefix
    ).order_by('-local_id')
    present_id = sports_grounds.values_list('local_id', flat=True)
    if present_id:
        return present_id[0] + 1
    else:
        return 1


class Reservation(models.Model):
    """
    Reservation of a specific SportsGround.
    Email, surname, start_time, end_time are required.
    Event_date and is_accepted fields are set automatically.
    """
    sports_ground = models.ForeignKey(
        SportsGround,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    email = models.EmailField()
    surname = models.CharField(max_length=40)
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_accepted = models.BooleanField(blank=True, default=False)
    
    ACCEPT = 1
    DELETE = 2
    ACTION_CHOICES = (
        (ACCEPT, 'Accept selected reservations'),
        (DELETE, 'Delete selected reservations'),
    )
    
    def __str__(self):
        event_time = str(self.start_time) + ' - ' + str(self.end_time)
        when = str(self.event_date) + ' ' + event_time
        return str(self.sports_ground) + ', ' + when
