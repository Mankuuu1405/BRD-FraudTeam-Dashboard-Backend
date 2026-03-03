from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.dateparse import parse_date
from cases.models import Case
from .serializers import ReportRequestSerializer


class GenerateReportView(APIView):

    def post(self, request):

        serializer = ReportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report_type = serializer.validated_data["report_type"]
        start_date = serializer.validated_data["start_date"]
        end_date = serializer.validated_data["end_date"]

        cases = Case.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )

        # 1️⃣ Fraud Summary Report
        if report_type == "FRAUD_SUMMARY":

            total_cases = cases.count()
            high_risk = cases.filter(fraud_score__gte=80).count()
            medium_risk = cases.filter(fraud_score__gte=50, fraud_score__lt=80).count()
            low_risk = cases.filter(fraud_score__lt=50).count()
            sanction_hits = cases.filter(aml_status="SANCTION_HIT").count()

            return Response({
                "report_type": "Fraud Summary Report",
                "date_range": f"{start_date} to {end_date}",
                "total_cases": total_cases,
                "high_risk": high_risk,
                "medium_risk": medium_risk,
                "low_risk": low_risk,
                "sanction_hits": sanction_hits,
            })

        # 2️⃣ AML Sanction Report
        elif report_type == "AML_SANCTION":

            sanction_cases = cases.filter(aml_status="SANCTION_HIT")

            data = sanction_cases.values(
                "case_id",
                "applicant_name",
                "fraud_score",
                "status",
                "created_at"
            )

            return Response({
                "report_type": "AML Sanction Report",
                "total_sanction_hits": sanction_cases.count(),
                "results": data
            })

        # 3️⃣ High Risk Applicants
        elif report_type == "HIGH_RISK":

            high_risk_cases = cases.filter(fraud_score__gte=80)

            data = high_risk_cases.values(
                "case_id",
                "applicant_name",
                "fraud_score",
                "aml_status",
                "status",
                "created_at"
            )

            return Response({
                "report_type": "High Risk Applicants",
                "total_high_risk": high_risk_cases.count(),
                "results": data
            })

        # 4️⃣ Synthetic ID Report
        elif report_type == "SYNTHETIC_ID":

            synthetic_cases = cases.filter(synthetic_id_status="SUSPECT")

            data = synthetic_cases.values(
                "case_id",
                "applicant_name",
                "fraud_score",
                "synthetic_id_status",
                "status",
                "created_at"
            )

            return Response({
                "report_type": "Synthetic ID Report",
                "total_suspects": synthetic_cases.count(),
                "results": data
            })