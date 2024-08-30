from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from django.core.exceptions import ValidationError


class Hotel(models.Model):
    name = models.CharField(_("Hotel name"), max_length=200)
    address = models.CharField(_("Hotel address"), max_length=250)
    email = models.EmailField(_("Hotel email"))
    stars = models.PositiveSmallIntegerField(default=0)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class RoomType(models.Model):
    name = models.CharField(_("Room name"), max_length=100)
    description = models.TextField(_("Description"), max_length=250)
    capacity = models.PositiveSmallIntegerField(_("Capacity"))

    def __str__(self):
        return self.name


class RoomRate(models.Model):
    room_type = models.ForeignKey(
        RoomType, related_name="room_rates", on_delete=models.CASCADE
    )
    rate = models.FloatField(_("Price per night"))
    date = models.DateField()

    def __str__(self):
        return str(self.id)


class Room(models.Model):
    hotel = models.ForeignKey(
        Hotel, related_name="hotel_rooms", on_delete=models.CASCADE
    )
    room_type = models.ForeignKey(
        RoomType, related_name="rooms", on_delete=models.CASCADE
    )
    description = models.TextField(max_length=250, blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=[("available", "Available"), ("occupied", "Occupied")]
    )

    def __str__(self):
        return f"{self.room_type.name} in {self.hotel.name}"


class Inventory(models.Model):
    hotel = models.ForeignKey(
        Hotel, related_name="inventories", on_delete=models.CASCADE
    )
    room_type = models.ForeignKey(
        RoomType, related_name="inventories", on_delete=models.CASCADE
    )
    available_rooms = models.PositiveSmallIntegerField()
    date = models.DateField()

    def __str__(self):
        return str(self.id)

    @property
    def total_rooms_for_type(self):
        return (
            Inventory.objects.filter(
                room_type=self.room_type, hotel=self.hotel
            ).aggregate(total_rooms=models.Sum("available_rooms"))["total_rooms"]
            or 0
        )

    @classmethod
    def total_rooms_by_room_type(cls, room_type_id):
        return (
            cls.objects.filter(room_type_id=room_type_id).aggregate(
                total_rooms=models.Sum("available_rooms")
            )["total_rooms"]
            or 0
        )

    @classmethod
    def total_rooms_by_hotel(cls, hotel_id):
        return (
            cls.objects.filter(hotel_id=hotel_id).aggregate(
                total_rooms=models.Sum("available_rooms")
            )["total_rooms"]
            or 0
        )


class Payment(models.Model):
    amount = models.FloatField()
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(
        max_length=50,
        choices=[("mpesa", "Mpesa"), ("paypal", "Paypal"), ("visa", "Visa")],
    )
    payment_status = models.CharField(max_length=30)

    def __str__(self):
        return f"Payment of {self.amount} made on {self.payment_date}"


class Booking(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="bookings", on_delete=models.CASCADE
    )
    hotel = models.ForeignKey(Hotel, related_name="bookings", on_delete=models.CASCADE)
    room_type = models.ForeignKey(
        RoomType, related_name="bookings", on_delete=models.CASCADE
    )
    payment = models.OneToOneField(
        Payment, related_name="booking", on_delete=models.CASCADE
    )
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_price = models.FloatField(blank=True, null=True)
    status = models.CharField(
        max_length=100,
        choices=[
            ("confirmed", "Confirmed"),
            ("cancelled", "Cancelled"),
            ("pending", "Pending"),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Booking by {self.user} for {self.room_type.name} at {self.hotel.name}"

    def save(self, *args, **kwargs):
        if not check_availability(
            self.room_type, self.check_in_date, self.check_out_date
        ):
            raise ValidationError(
                "The room type is not available for the selected dates."
            )
        self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)

    def calculate_total_price(self):
        rate = RoomRate.objects.filter(
            room_type=self.room_type,
            date__gte=self.check_in_date,
            date__lt=self.check_out_date,
        ).aggregate(total_rate=models.Sum("rate"))["total_rate"]
        if rate:
            return rate
        days = (self.check_out_date - self.check_in_date).days
        average_rate = RoomRate.objects.filter(room_type=self.room_type).aggregate(
            avg_rate=models.Avg("rate")
        )["avg_rate"]
        return days * average_rate if average_rate else 0

    @property
    def duration(self):
        return (self.check_out_date - self.check_in_date).days


# Utility function to check if the booking dates overlap with any existing bookings
def check_availability(room_type, check_in_date, check_out_date):
    overlapping_bookings = Booking.objects.filter(
        room_type=room_type,
        check_in_date__lt=check_out_date,
        check_out_date__gt=check_in_date,
    ).exists()
    return not overlapping_bookings
