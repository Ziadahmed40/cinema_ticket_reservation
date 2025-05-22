from datetime import datetime

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Movie, Showtime, Seat, Reservation, Profile
from .serializers import (
    MovieSerializer, ShowtimeSerializer, SeatSerializer,
    ReservationSerializer, ProfileSerializer, UserRegistrationSerializer
)
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction


class MovieList(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.AllowAny]


class ShowtimeList(generics.ListAPIView):
    queryset = Showtime.objects.all()
    serializer_class = ShowtimeSerializer
    permission_classes = [permissions.AllowAny]


class ReserveSeats(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        showtime_id = request.data.get('showtime_id')
        seat_ids = request.data.get('seat_ids')

        if not showtime_id or not seat_ids:
            return Response({"error": "showtime_id and seat_ids are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(seat_ids, list) or not all(isinstance(seat_id, int) for seat_id in seat_ids):
            return Response({"error": "seat_ids must be a list of integers."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            showtime = Showtime.objects.get(id=showtime_id)
        except Showtime.DoesNotExist:
            return Response({"error": "Showtime not found."},
                            status=status.HTTP_404_NOT_FOUND)

        available_seats = Seat.objects.filter(showtime=showtime, is_reserved=False, id__in=seat_ids)

        if available_seats.count() != len(seat_ids):
            return Response({"error": "One or more selected seats are already reserved."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                reservation = Reservation.objects.create(user=request.user, showtime=showtime)
                for seat in available_seats:
                    seat.is_reserved = True
                    seat.save()
                reservation.seats.set(available_seats)
                reservation.save()


                # try:
                #     send_mail(
                #         'Booking Confirmed',
                #         f'Your seats for {showtime.movie.title} at {showtime.start_time} are booked.',
                #         'noreply@cinema.com',
                #         [request.user.email],
                #         fail_silently=True,
                #     )
                # except Exception as e:
                #     print(f"Email failed: {e}")

                return Response({'message': 'Reservation successful!'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"Reservation failed: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MyProfile(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
            reservations = Reservation.objects.filter(user=request.user)
            return Response({
                'profile': ProfileSerializer(profile).data,
                'reservations': ReservationSerializer(reservations, many=True).data
            })
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)


class UserRegistration(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AvailableShowtimes(APIView):
    def get(self, request, movie_id):
        try:
            current_time = datetime.now()
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            genre = request.query_params.get('genre')

            showtimes = Showtime.objects.filter(movie_id=movie_id, start_time__gt=current_time)

            if start_date and end_date:
                try:
                    showtimes = showtimes.filter(start_time__range=[start_date, end_date])
                except Exception:
                    return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'},
                                    status=status.HTTP_400_BAD_REQUEST)

            if genre:
                showtimes = showtimes.filter(movie__genre__iexact=genre)

            if not showtimes.exists():
                return Response({'message': 'No available showtimes found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = ShowtimeSerializer(showtimes, many=True)
            return Response({'available_showtimes': serializer.data})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CancelReservation(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, reservation_id):
        try:
            reservation = Reservation.objects.get(id=reservation_id, user=request.user)
        except Reservation.DoesNotExist:
            return Response({'error': 'Reservation not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            send_mail(
                'Reservation Canceled',
                f'Your reservation for {reservation.showtime.movie.title} at {reservation.showtime.start_time} has been canceled.',
                'noreply@cinema.com',
                [reservation.user.email],
                fail_silently=True
            )
        except Exception as e:
            print(f"Failed to send cancellation email: {e}")

        reservation.delete()
        return Response({'message': 'Reservation canceled.'})


class GetAvailableSeats(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, movie_id, showtime_id):
        try:
            showtime = Showtime.objects.get(id=showtime_id, movie_id=movie_id)
        except Showtime.DoesNotExist:
            return Response({'error': 'Showtime or Movie not found.'}, status=status.HTTP_404_NOT_FOUND)

        available_seats = Seat.objects.filter(showtime=showtime, is_reserved=False)

        available_seats_data = [{
            "row": seat.row,
            "number": seat.number,
            "id": seat.id
        } for seat in available_seats]

        return Response({
            "movie_title": showtime.movie.title,
            "showtime_start": showtime.start_time,
            "available_seats": available_seats_data
        })
