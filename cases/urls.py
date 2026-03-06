from django.urls import path
from . import views
from .views import CreateCaseView, CaseListView, CaseDetailView, UpdateCaseStatusAPIView

urlpatterns = [
    path("create/", CreateCaseView.as_view(), name="create_case"),
    path("list/", CaseListView.as_view(), name="list_cases"),
    path("<str:case_id>/", CaseDetailView.as_view(), name="case_detail_api"),
    path("<str:case_id>/action/<str:action>/", UpdateCaseStatusAPIView.as_view(), name="update_case_status_api"),

    path("case/<str:case_id>/", views.case_detail, name="case_detail"),
    path("case/<str:case_id>/action/<str:action>/", views.update_case_status, name="update_case_status"),
]

