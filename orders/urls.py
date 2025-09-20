from django.urls import path
from .views import (
    OrderListView, OrderDetailView, DashboardView,
    AssignDeliveryView, OrderTrackingView
)

urlpatterns = [
    path("", OrderListView.as_view()),
    path("<str:pk>/", OrderDetailView.as_view()),
    path("<str:pk>/tracking/", OrderTrackingView.as_view()),
    path("assign/", AssignDeliveryView.as_view()),
    path("dashboard/", DashboardView.as_view()),
]