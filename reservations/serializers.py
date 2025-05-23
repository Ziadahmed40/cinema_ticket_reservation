from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Movie, Screen, Showtime, Seat, Reservation, Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    favorite_genre = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'full_name', 'phone', 'favorite_genre']

    def create(self, validated_data):

        full_name = validated_data.pop('full_name')
        phone = validated_data.pop('phone')
        favorite_genre = validated_data.pop('favorite_genre', '')


        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        # Create the profile
        Profile.objects.create(
            user=user,
            full_name=full_name,
            phone=phone,
            favorite_genre=favorite_genre
        )

        return user

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['user', 'full_name', 'phone', 'favorite_genre']


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'


class ScreenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screen
        fields = '__all__'


class ShowtimeSerializer(serializers.ModelSerializer):
    movie = MovieSerializer()
    screen = ScreenSerializer()

    class Meta:
        model = Showtime
        fields = '__all__'


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = '__all__'


class ReservationSerializer(serializers.ModelSerializer):
    seats = SeatSerializer(many=True)
    showtime = ShowtimeSerializer()

    class Meta:
        model = Reservation
        fields = ['id', 'showtime', 'seats', 'reserved_at']
