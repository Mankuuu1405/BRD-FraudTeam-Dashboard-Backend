from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from cases.models import Case
from Analytics.models import Case as AnalyticsCase
from .models import Report
from .serializers import ReportRequestSerializer, ReportHistorySerializer


class ReportHistoryView(APIView):
    def get(self, request):
        reports = Report.objects.filter(generated_by=request.user).order_by("-created_at")
        serializer = ReportHistorySerializer(reports, many=True)
        return Response(serializer.data)

class GenerateReportView(APIView):
    def post(self, request):
        serializer = ReportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report_type = serializer.validated_data["report_type"]
        start_date = serializer.validated_data["start_date"]
        end_date = serializer.validated_data["end_date"]

        report = Report.objects.create(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            generated_by=request.user,
        )

        # Query standard cases
        cases = Case.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        # Query analytics cases
        a_cases = AnalyticsCase.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )

        # 1️⃣ Fraud Summary Report
        if report_type == "FRAUD_SUMMARY":
            total_cases = cases.count() + a_cases.count()
            
            # Risk counts from standard cases
            high_risk = cases.filter(fraud_score__gte=80).count()
            medium_risk = cases.filter(fraud_score__gte=50, fraud_score__lt=80).count()
            low_risk = cases.filter(fraud_score__lt=50).count()
            
            # Risk counts from analytics cases
            high_risk += a_cases.filter(risk_level="HIGH").count()
            medium_risk += a_cases.filter(risk_level="MEDIUM").count()
            low_risk += a_cases.filter(risk_level="LOW").count()
            
            sanction_hits = cases.filter(aml_status="SANCTION_HIT").count() + a_cases.filter(is_aml_hit=True).count()

            return Response({
                "report_id": report.id,
                "report_type": "Fraud Summary Report",
                "date_range": f"{start_date} to {end_date}",
                "total_cases": total_cases,
                "high_risk": high_risk,
                "medium_risk": medium_risk,
                "low_risk": low_risk,
                "sanction_hits": sanction_hits,
            })

        # Helper to format combined results
        def get_results_list(c_qs, a_qs, filter_type=None):
            results = []
            
            # Standard Cases
            for c in c_qs:
                results.append({
                    "case_id": c.case_id,
                    "name": c.name,
                    "fraud_score": c.fraud_score,
                    "aml_status": c.aml_status,
                    "synthetic_status": c.synthetic_status,
                    "status": c.status,
                    "created_at": c.created_at
                })
            
            # Analytics Cases
            for ac in a_qs:
                results.append({
                    "case_id": f"AC-{ac.id}",
                    "name": ac.customer_name,
                    "fraud_score": int((ac.fraud_probability or 0) * 100),
                    "aml_status": "SANCTION_HIT" if ac.is_aml_hit else "CLEAR",
                    "synthetic_status": "SUSPECT" if ac.is_synthetic_id else "CLEAN",
                    "status": "ANALYTICS",
                    "created_at": ac.created_at
                })
            return results

        # 2️⃣ AML Sanction Report
        if report_type == "AML_SANCTION":
            c_hits = cases.filter(aml_status="SANCTION_HIT")
            a_hits = a_cases.filter(is_aml_hit=True)
            results = get_results_list(c_hits, a_hits)
            
            return Response({
                "report_id": report.id,
                "report_type": "AML Sanction Report",
                "total_sanction_hits": len(results),
                "results": results
            })

        # 3️⃣ High Risk Applicants
        elif report_type == "HIGH_RISK":
            c_high = cases.filter(fraud_score__gte=80)
            a_high = a_cases.filter(risk_level="HIGH")
            results = get_results_list(c_high, a_high)
            
            return Response({
                "report_id": report.id,
                "report_type": "High Risk Applicants",
                "total_high_risk": len(results),
                "results": results
            })

        # 4️⃣ Synthetic ID Report
        elif report_type == "SYNTHETIC_ID":
            c_sus = cases.filter(synthetic_status="SUSPECT")
            a_sus = a_cases.filter(is_synthetic_id=True)
            results = get_results_list(c_sus, a_sus)
            
            return Response({
                "report_id": report.id,
                "report_type": "Synthetic ID Report",
                "total_suspects": len(results),
                "results": results
            })

        # 5️⃣ All Case Records
        elif report_type == "ALL_CASES":
            results = get_results_list(cases, a_cases)
            return Response({
                "report_id": report.id,
                "report_type": "All Case Records",
                "total_records": len(results),
                "results": results
            })