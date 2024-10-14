from django.conf import settings
from django.db import models


class ShowTheme(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class AstronomyShow(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    show_theme = models.ManyToManyField(
        ShowTheme, related_name="astronomy_shows"
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=255, unique=True)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return f"{self.name}: {self.rows} rows x {self.seats_in_row} seats"


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(
        AstronomyShow, on_delete=models.CASCADE, related_name="sessions",
    )
    planetarium_dome = models.ForeignKey(
        PlanetariumDome, on_delete=models.CASCADE, related_name="sessions",
    )
    show_time = models.DateTimeField()

    class Meta:
        ordering = ["-show_time"]

    def __str__(self):
        return f"{self.astronomy_show.title} {str(self.show_time)}"


class Reservation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.created_at)


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    show_session = models.ForeignKey(
        ShowSession, on_delete=models.CASCADE, related_name="tickets",
    )
    reservation = models.ForeignKey(
        Reservation, on_delete=models.CASCADE, related_name="tickets",
    )

    class Meta:
        ordering = ["row", "seat"]
        constraints = [models.UniqueConstraint(
            fields=["row", "seat", "show_session"],
            name="unique_ticket",
        )]

    def __str__(self):
        return f"{self.row} {self.seat} {self.show_session}"

    @staticmethod
    def validate_position(
            field: str,
            position: int,
            position_limit: int,
            error_to_raise
    ):
        if not (1 <= position <= position_limit):
            raise error_to_raise(
                {field: f"{field.capitalize()} must be in range: "
                 f"1 - {position_limit}, not {position}"}
            )

    def clean(self):
        Ticket.validate_position(
            "seat",
            self.seat,
            self.show_session.planetarium_dome.seats_in_row,
            ValueError
        )
        Ticket.validate_position(
            "row",
            self.row,
            self.show_session.planetarium_dome.rows,
            ValueError
        )

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )
