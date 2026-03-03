from django.urls import path
from . import views
from .views import EditProfileView

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/settings/profile/edit/', EditProfileView.as_view()),
]
