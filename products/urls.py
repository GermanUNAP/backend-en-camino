from django.urls import path
from .views import ProductListView, ProductDetailView

urlpatterns = [
    path("", ProductListView.as_view()),
    path("<str:pk>/", ProductDetailView.as_view()),
]