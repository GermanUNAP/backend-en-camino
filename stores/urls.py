from django.urls import path
from .views import StoreListView, StoreDetailView, CityListView

urlpatterns = [
    path("", StoreListView.as_view()),
    path("<str:pk>/", StoreDetailView.as_view()),
    path("cities/", CityListView.as_view()),
]