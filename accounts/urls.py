from django.urls import path
from .views import UserListView, UserDetailView, ProfileListView, ProfileDetailView

urlpatterns = [
    path("users/", UserListView.as_view()),
    path("users/<int:pk>/", UserDetailView.as_view()),
    path("profiles/", ProfileListView.as_view()),
    path("profiles/<int:pk>/", ProfileDetailView.as_view()),
]