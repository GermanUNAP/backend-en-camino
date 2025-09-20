from django.urls import path
from .views import PaymentListView, PaymentDetailView, ProcessPaymentView, UploadYapeProofView

urlpatterns = [
    path("", PaymentListView.as_view()),
    path("<str:pk>/", PaymentDetailView.as_view()),
    path("process/", ProcessPaymentView.as_view()),
    path("yape/upload/", UploadYapeProofView.as_view()),
]