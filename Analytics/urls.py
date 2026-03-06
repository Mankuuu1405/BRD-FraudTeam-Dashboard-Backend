from django.urls import path
from .views import CreateCaseView, DashboardAnalyticsView

urlpatterns = [
    path("create-case/", CreateCaseView.as_view(), name="analytics-create-case"),
    path("dashboard/", DashboardAnalyticsView.as_view(), name="analytics-dashboard"),
]
