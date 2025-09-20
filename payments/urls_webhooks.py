from django.urls import path
from .views import CulqiWebhookView

urlpatterns = [
    path("", CulqiWebhookView.as_view(), name="culqi_webhook"),
]