from django.urls import path
from .views import (
    HotelListCreateView,
    HotelRetrieveUpdateDestroyView,
    RoomTypeListCreateView,
    RoomTypeRetrieveUpdateDestroyView,
    RoomRateListCreateView,
    RoomRateRetrieveUpdateDestroyView,
    RoomListCreateView,
    RoomRetrieveUpdateDestroyView,
    InventoryListCreateView,
    InventoryRetrieveUpdateDestroyView,
    PaymentListCreateView,
    PaymentRetrieveUpdateDestroyView,
    BookingListCreateView,
    BookingRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("hotels/", HotelListCreateView.as_view(), name="hotel-list-create"),
    path(
        "hotels/<int:pk>/",
        HotelRetrieveUpdateDestroyView.as_view(),
        name="hotel-detail",
    ),
    path("roomtypes/", RoomTypeListCreateView.as_view(), name="roomtype-list-create"),
    path(
        "roomtypes/<int:pk>/",
        RoomTypeRetrieveUpdateDestroyView.as_view(),
        name="roomtype-detail",
    ),
    path("roomrates/", RoomRateListCreateView.as_view(), name="roomrate-list-create"),
    path(
        "roomrates/<int:pk>/",
        RoomRateRetrieveUpdateDestroyView.as_view(),
        name="roomrate-detail",
    ),
    path("rooms/", RoomListCreateView.as_view(), name="room-list-create"),
    path(
        "rooms/<int:pk>/", RoomRetrieveUpdateDestroyView.as_view(), name="room-detail"
    ),
    path(
        "inventories/", InventoryListCreateView.as_view(), name="inventory-list-create"
    ),
    path(
        "inventories/<int:pk>/",
        InventoryRetrieveUpdateDestroyView.as_view(),
        name="inventory-detail",
    ),
    path("payments/", PaymentListCreateView.as_view(), name="payment-list-create"),
    path(
        "payments/<int:pk>/",
        PaymentRetrieveUpdateDestroyView.as_view(),
        name="payment-detail",
    ),
    path("bookings/", BookingListCreateView.as_view(), name="booking-list-create"),
    path(
        "bookings/<int:pk>/",
        BookingRetrieveUpdateDestroyView.as_view(),
        name="booking-detail",
    ),
]
