from django.urls import path
from .views import SubscriptionPlanListView, SubscriptionPlanDetailView, PlanDefinitionListView, ProcessSubscriptionPaymentView

urlpatterns = [
    path("subscriptions/", SubscriptionPlanListView.as_view()),
    path("subscriptions/<str:pk>/", SubscriptionPlanDetailView.as_view()),
    path("definitions/", PlanDefinitionListView.as_view()),
    path("process/", ProcessSubscriptionPaymentView.as_view()),
]