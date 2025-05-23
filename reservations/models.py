from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.IntegerField()  # in minutes
    genre = models.CharField(max_length=50)
    image_url = models.CharField(max_length=255, blank=True, null=True)
    rating=models.FloatField()
    def __str__(self):
        return self.title

class Screen(models.Model):
    number = models.IntegerField()
    total_seats = models.IntegerField()

    def __str__(self):
        return f"Screen {self.number}"

class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE)
    start_time = models.DateTimeField()

    def __str__(self):
        return f"{self.movie.title} at {self.start_time}"

class Seat(models.Model):
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    row = models.CharField(max_length=1)
    number = models.IntegerField()
    is_reserved = models.BooleanField(default=False)

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    seats = models.ManyToManyField(Seat)
    reserved_at = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    favorite_genre = models.CharField(max_length=50, blank=True)

class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)

@receiver(post_save, sender=Showtime)
def create_seats_for_showtime(sender, instance, created, **kwargs):
    if created and not Seat.objects.filter(showtime=instance).exists():
        rows = 'ABCDEFGHIJ'  # 10 rows
        seats_per_row = 10  # 10 seats per row
        for row in rows:
            for num in range(1, seats_per_row + 1):
                Seat.objects.create(showtime=instance, row=row, number=num)
