from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

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


class ShowSessionRetrieveSerializer(ShowSessionSerializer):
    astronomy_show = AstronomyShowRetrieveSerializer(many=False)
    planetarium_dome = PlanetariumDomeSerializer(many=False)


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "show_session"]
        validators = [UniqueTogetherValidator(
            queryset=Ticket.objects.all(),
            fields=["row", "seat", "show_session"],
            message="A ticket with this seat-row "
                    "for this show session already reserved."
        )]


    def validate(self, attrs):
        Ticket.validate_position(
            "seat",
            attrs["seat"],
            attrs["show_session"].planetarium_dome.seats_in_row,
            serializers.ValidationError
        )
        Ticket.validate_position(
            "row",
            attrs["row"],
            attrs["show_session"].planetarium_dome.rows,
            serializers.ValidationError
        )
        return attrs


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)
    class Meta:
        model = Reservation
        fields = ["id", "created_at", "tickets"]

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation
