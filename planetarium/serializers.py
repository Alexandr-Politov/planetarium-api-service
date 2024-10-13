from rest_framework import serializers

from planetarium.models import (
    AstronomyShow,
    ShowTheme,
    PlanetariumDome,
    ShowSession,
    Ticket,
    Reservation
)


class ShowThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = ["id", "name"]


class AstronomyShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow
        fields = ["id", "title", "description", "show_theme"]


class AstronomyShowRetrieveSerializer(AstronomyShowSerializer):
    show_theme = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )

class AstronomyShowCreateSerializer(AstronomyShowSerializer):
    show_theme = serializers.PrimaryKeyRelatedField(
        queryset=ShowTheme.objects.all(), many=True
    )


class PlanetariumDomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = ["id", "name", "rows", "seats_in_row", "capacity"]


class ShowSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSession
        fields = ["id", "astronomy_show", "planetarium_dome", "show_time"]


class ShowSessionListSerializer(ShowSessionSerializer):
    astronomy_show = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="title"
    )
    planetarium_dome = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )
    show_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "show_session"]


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ["id", "user", "created_at"]
