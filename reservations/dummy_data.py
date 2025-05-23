from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from .models import Movie, Screen, Showtime, Seat, Reservation, Profile, UserRole

def create_dummy_data():
    print("🧹 Deleting old data...")

    # Delete from dependent to independent to avoid FK constraint issues
    Reservation.objects.all().delete()
    Seat.objects.all().delete()
    Showtime.objects.all().delete()
    Movie.objects.all().delete()
    Screen.objects.all().delete()
    Profile.objects.all().delete()
    UserRole.objects.all().delete()

    # Only delete non-superuser users (keep admin access)
    User.objects.exclude(is_superuser=True).delete()

    print("✅ All old data cleared.")
    # Create users (if they don't already exist)
    user1, _ = User.objects.get_or_create(username='john_doe', email='john@example.com')
    user1.set_password("password123")
    user1.save()

    user2, _ = User.objects.get_or_create(username='jane_smith', email='jane@example.com')
    user2.set_password("password123")
    user2.save()

    # Create profiles
    Profile.objects.get_or_create(user=user1,
                                  defaults={"full_name": "John Doe", "phone": "1234567890", "favorite_genre": "Action"})
    Profile.objects.get_or_create(user=user2, defaults={"full_name": "Jane Smith", "phone": "0987654321",
                                                        "favorite_genre": "Comedy"})

    # 1. Create Screens
    screen1 = Screen.objects.create(number=1, total_seats=100)
    screen2 = Screen.objects.create(number=2, total_seats=100)

    # 2. Create Movies
    action = Movie.objects.create(title="Action Movie", description="Boom boom", duration=120, genre="Action", image_url="", rating=4.5)
    comedy = Movie.objects.create(title="Comedy Movie", description="Haha", duration=90, genre="Comedy", image_url="", rating=4.2)
    drama = Movie.objects.create(title="Drama Movie", description="Tears and hugs", duration=110, genre="Drama", image_url="", rating=3.8)

    # 3. Create Showtimes (auto-generates 100 seats each)
    now = timezone.now()
    showtimes = [
        Showtime.objects.create(movie=action, screen=screen1, start_time=now + timedelta(hours=2)),
        Showtime.objects.create(movie=action, screen=screen2, start_time=now + timedelta(hours=4)),
        Showtime.objects.create(movie=comedy, screen=screen1, start_time=now + timedelta(hours=1)),
        Showtime.objects.create(movie=comedy, screen=screen2, start_time=now + timedelta(hours=3)),
        Showtime.objects.create(movie=drama, screen=screen1, start_time=now + timedelta(hours=5)),
        Showtime.objects.create(movie=drama, screen=screen2, start_time=now + timedelta(hours=6)),
    ]

    # # 4. Create Users with Profiles and Roles
    # user1 = User.objects.create_user(username="ahmed", email="ahmed@example.com", password="password123")
    # Profile.objects.create(user=user1, full_name="Ahmed Ali", phone="0123456789", favorite_genre="Action")
    # UserRole.objects.create(user=user1, is_admin=False)
    #
    # user2 = User.objects.create_user(username="mona", email="mona@example.com", password="password123")
    # Profile.objects.create(user=user2, full_name="Mona Said", phone="01122334455", favorite_genre="Comedy")
    # UserRole.objects.create(user=user2, is_admin=True)

    # 5. Reserve a few seats for each user
    for user, showtime in zip([user1, user2], showtimes[:2]):
        available = Seat.objects.filter(showtime=showtime, is_reserved=False)[:2]
        reservation = Reservation.objects.create(user=user, showtime=showtime)
        for seat in available:
            seat.is_reserved = True
            seat.save()
        reservation.seats.set(available)

    print("✅ Dummy data created successfully!")
