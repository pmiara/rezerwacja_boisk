from django.db import models


class Administrator(models.Model):
    """
    Administrator of a Place.
    TODO: Administrator can perform following actions:
    ...
    """
    name = models.CharField(max_length=40, primary_key=True)
    def __str__(self):
        return self.name


class Place(models.Model):
    """
    Place is a location with sports grounds. Administrator is a person
    who can edit info about a Place and manage registrations.
    """
    name = models.CharField(max_length=40, primary_key=True)
    administrator = models.ForeignKey(
        Administrator,
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
    a winter.
    """
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name='sports_grounds'
    )
    local_id = models.PositiveIntegerField(blank=True)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    start_season_date = models.DateTimeField(blank=True)
    end_season_date = models.DateTimeField(blank=True)
    
    def __str__(self):
        return "Boisko nr " + str(self.local_id)
    
    def save(self, *args, **kwargs):
        self.local_id = get_local_id(self.place)
        super(SportsGround, self).save(*args, **kwargs)


def get_local_id(place):
    sports_grounds = place.sports_grounds.all().order_by('-local_id')
    present_id = sports_grounds.values_list('local_id', flat=True)
    if present_id:
        return present_id[0] + 1
    else:
        return 1
