from django.urls import path
from .views import MovieList, ShowtimeList, ReserveSeats, MyProfile, UserRegistration, AvailableShowtimes, \
    GetAvailableSeats
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('movies/', MovieList.as_view()),
    path('showtimes/', ShowtimeList.as_view()),
    path('reserve/', ReserveSeats.as_view()),
    path('profile/', MyProfile.as_view()),
    path('register/', UserRegistration.as_view(), name='user_register'),
    path('movies/<int:movie_id>/available-showtimes/', AvailableShowtimes.as_view(), name='available_showtimes'),
    path('available-seats/<int:movie_id>/<int:showtime_id>/', GetAvailableSeats.as_view(), name='get_available_seats'),
]
