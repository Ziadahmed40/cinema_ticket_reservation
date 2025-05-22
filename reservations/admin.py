from django.contrib import admin
from .models import Movie, Screen, Showtime, Seat, Reservation, Profile

admin.site.register(Movie)
admin.site.register(Screen)
admin.site.register(Showtime)
admin.site.register(Seat)
admin.site.register(Reservation)
admin.site.register(Profile)
