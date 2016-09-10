from django.db import models



class Administrator(models.Model):
    """
    Administrator of a Place.
    TODO: Administrator can perform following actions:
    ...
    """
    name = models.CharField(max_length=40, primary_key=True)


class Place(models.Model):
    """
    Place is a location with pitches/courts. Administrator is a person
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
