from django.urls import path
from .views import (
    DeliveryPointListView, DeliveryPointDetailView, 
    ShipperListView, ShipperDetailView, ShipperDashboardView,
    UpdateShipperLocationView, CreateTrackingEventView,
    DeliveryPointOrdersView
)

urlpatterns = [
    path("points/", DeliveryPointListView.as_view()),
    path("points/<str:pk>/", DeliveryPointDetailView.as_view()),
    path("points/<str:pk>/orders/", DeliveryPointOrdersView.as_view()),
    path("shippers/", ShipperListView.as_view()),
    path("shippers/<str:pk>/", ShipperDetailView.as_view()),
    path("shippers/dashboard/", ShipperDashboardView.as_view()),
    path("shippers/<str:pk>/location/", UpdateShipperLocationView.as_view()),
    path("tracking/events/", CreateTrackingEventView.as_view()),
]