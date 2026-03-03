# from rest_framework.routers import DefaultRouter
# from .views import CaseViewSet

# router = DefaultRouter()
# router.register(r'cases', CaseViewSet)

# urlpatterns = router.urls

from django.urls import path
from . import views

urlpatterns = [
    path("case/<str:case_id>/", views.case_detail, name="case_detail"),
    path("case/<str:case_id>/action/<str:action>/", views.update_case_status, name="update_case_status"),
]

from django.urls import path
from .views import CreateCaseView, CaseListView, CaseDetailView

urlpatterns = [
    path("create/", CreateCaseView.as_view()),
    path("list/", CaseListView.as_view()),
    path("<str:case_id>/", CaseDetailView.as_view()),
]

