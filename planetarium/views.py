from django.db.models import Count, F
from rest_framework import viewsets

from planetarium.models import (
    AstronomyShow,
    ShowTheme,
    PlanetariumDome,
    ShowSession,
    Reservation,
)
from planetarium.serializers import (
    AstronomyShowRetrieveSerializer,
    AstronomyShowCreateSerializer,
    ShowThemeSerializer,
    PlanetariumDomeSerializer,
    ShowSessionSerializer,
    ShowSessionListSerializer,
    ShowSessionRetrieveSerializer,
    ReservationListSerializer,
    ReservationRetrieveSerializer,
    ReservationCreateSerializer,
)


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.all()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return AstronomyShowRetrieveSerializer
        if self.action in ("create", "update", "partial_update"):
            return AstronomyShowCreateSerializer

    def separate_ids(self, string: str):
        return [int(str_id) for str_id in string.split(",")]

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            queryset = queryset.prefetch_related("show_theme")
            show_themes = self.request.query_params.get("show_theme", None)
            title = self.request.query_params.get("title")
            if show_themes:
                show_theme_ids = self.separate_ids(show_themes)
                queryset = queryset.filter(show_theme__id__in=show_theme_ids)
            if title:
                queryset = queryset.filter(title__icontains=title)
            return queryset.distinct()

        if self.action == "retrieve":
            return queryset.prefetch_related("show_theme")
        
        return self.queryset


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.select_related()

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        if self.action == "retrieve":
            return ShowSessionRetrieveSerializer
        return ShowSessionSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = queryset.annotate(
                tickets_available=F("planetarium_dome__rows")
                                  * F("planetarium_dome__seats_in_row")
                                  - Count("tickets")
            )
        return queryset


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        if self.action == "retrieve":
            return ReservationRetrieveSerializer
        if self.action == "create":
            return ReservationCreateSerializer
        return ReservationListSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
