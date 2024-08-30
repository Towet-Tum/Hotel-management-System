from django.contrib import admin
from core.models import Hotel, Room, RoomRate, Inventory, Payment, Booking, RoomType

# Register your models here.
admin.site.register(Hotel)
admin.site.register(Room)
admin.site.register(RoomType)
admin.site.register(RoomRate)
admin.site.register(Inventory)
admin.site.register(Payment)
admin.site.register(Booking)
