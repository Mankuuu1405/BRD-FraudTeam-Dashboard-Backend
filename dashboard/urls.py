from django.urls import path
from .views import EditProfileView, AnalyticsDashboardView

urlpatterns = [
    path('dashboard/', AnalyticsDashboardView.as_view(), name='dashboard-api'),
    path('analytics/', AnalyticsDashboardView.as_view(), name='analytics-api'),
    path('settings/profile/edit/', EditProfileView.as_view()),
]
