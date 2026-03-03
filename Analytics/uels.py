from django.urls import path
from .views import CreateCaseView, AnalyticsDashboardView

urlpatterns = [
    path("create-case/", CreateCaseView.as_view()),
    path("dashboard/", AnalyticsDashboardView.as_view()),
]