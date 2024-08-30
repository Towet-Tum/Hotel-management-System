from rest_framework import serializers
from .models import Hotel, RoomType, RoomRate, Room, Inventory, Payment, Booking
from .models import check_availability


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = [
            "id",
            "name",
            "address",
            "email",
            "stars",
            "check_in_time",
            "check_out_time",
        ]


class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ["id", "name", "description", "capacity"]


class RoomRateSerializer(serializers.ModelSerializer):
    room_type = RoomTypeSerializer(read_only=True)

    class Meta:
        model = RoomRate
        fields = ["id", "room_type", "rate", "date"]


class RoomSerializer(serializers.ModelSerializer):
    hotel = HotelSerializer(read_only=True)
    room_type = RoomTypeSerializer(read_only=True)

    class Meta:
        model = Room
        fields = ["id", "hotel", "room_type", "description", "status"]


class InventorySerializer(serializers.ModelSerializer):
    hotel = HotelSerializer(read_only=True)
    room_type = RoomTypeSerializer(read_only=True)

    class Meta:
        model = Inventory
        fields = ["id", "hotel", "room_type", "available_rooms", "date"]

    def validate(self, data):
        if data["available_rooms"] < 0:
            raise serializers.ValidationError("Available rooms cannot be negative.")
        return data


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "amount", "payment_date", "payment_method", "payment_status"]


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    hotel = HotelSerializer(read_only=True)
    room_type = RoomTypeSerializer(read_only=True)
    payment = PaymentSerializer()
    duration = serializers.IntegerField(source="duration", read_only=True)
    total_price = serializers.FloatField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "user",
            "hotel",
            "room_type",
            "payment",
            "check_in_date",
            "check_out_date",
            "total_price",
            "status",
            "created_at",
            "duration",
        ]
        read_only_fields = ["created_at", "total_price"]

    def create(self, validated_data):
        payment_data = validated_data.pop("payment")
        payment = Payment.objects.create(**payment_data)
        booking = Booking.objects.create(payment=payment, **validated_data)
        return booking

    def update(self, instance, validated_data):
        payment_data = validated_data.pop("payment", None)
        if payment_data:
            Payment.objects.filter(pk=instance.payment.pk).update(**payment_data)
        return super().update(instance, validated_data)

    def validate(self, data):
        if data["check_in_date"] >= data["check_out_date"]:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date."
            )
        if not check_availability(
            data["room_type"], data["check_in_date"], data["check_out_date"]
        ):
            raise serializers.ValidationError(
                "The room type is not available for the selected dates."
            )
        return data
