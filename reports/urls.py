from django.urls import path
from .views import GenerateReportView, ReportHistoryView

urlpatterns = [
    path("generate/", GenerateReportView.as_view(), name="generate-report"),
    path("history/", ReportHistoryView.as_view(), name="report-history"),
]