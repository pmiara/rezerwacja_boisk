from django.contrib import admin
from .models import Administrator, Place, SportsGround, Reservation


admin.site.register(Administrator)
admin.site.register(Place)
admin.site.register(SportsGround)
admin.site.register(Reservation)
