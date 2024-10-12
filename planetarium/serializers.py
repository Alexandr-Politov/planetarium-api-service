from rest_framework import serializers
from rest_framework.fields import SlugField
from rest_framework.relations import PrimaryKeyRelatedField

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
    show_theme = SlugField(source="show_theme.name")


class AstronomyShowCreateSerializer(AstronomyShowSerializer):
    show_theme = PrimaryKeyRelatedField(queryset=ShowTheme.objects.all())


class PlanetariumDomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = ["id", "name", "rows", "seats_in_row", "capacity"]


class ShowSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSession
        fields = ["id", "astronomy_show", "planetarium_dome", "show_time"]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "show_session"]


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ["id", "user", "created_at"]
