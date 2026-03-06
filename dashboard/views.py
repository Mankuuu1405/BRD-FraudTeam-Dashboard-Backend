from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from collections import defaultdict

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Applicant, Alert
from cases.models import Case  # Using the primary Case model
from Analytics.models import Case as AnalyticsCase
from .serializers import EditProfileSerializer


class EditProfileView(APIView):
    """
    PATCH /api/settings/profile/edit/
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = EditProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Profile updated successfully."},
            status=status.HTTP_200_OK
        )


# -------------------------
# TEMPLATE DASHBOARD VIEW
# -------------------------

def dashboard(request):
    applicants = Applicant.objects.all().order_by('-created_at')
    alerts = Alert.objects.all().order_by('-created_at')[:5]

    fraud_score_avg = (
        sum([a.fraud_score for a in applicants]) / applicants.count()
        if applicants.exists() else 0
    )

    synthetic_id_alerts = alerts.filter(alert_type='DOC_MISMATCH').count()
    aml_hits = applicants.filter(aml_status='HIT').count()
    behavioral_flags = alerts.filter(alert_type='HIGH_FRAUD').count()
    pattern_matches = alerts.filter(alert_type='AML_MATCH').count()

    context = {
        'fraud_score_avg': round(fraud_score_avg),
        'synthetic_id_alerts': synthetic_id_alerts,
        'aml_hits': aml_hits,
        'behavioral_flags': behavioral_flags,
        'pattern_matches': pattern_matches,
        'high_risk_applicants': applicants.filter(fraud_score__gte=75),
        'recent_alerts': alerts,
    }

    return render(request, 'bashboard/dashboard.html', context)


# -------------------------
# API DASHBOARD VIEW (DRF)
# -------------------------

class AnalyticsDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        def _risk_from_score(score):
            if score is None:
                return "LOW"
            if score >= 70:
                return "HIGH"
            if score >= 40:
                return "MEDIUM"
            return "LOW"

        def _normalize_aml(value):
            return "HIT" if value in ("HIT", "SANCTION_HIT") else "CLEAR"

        last_7_days = timezone.now() - timedelta(days=7)

        risk_counts = defaultdict(int)
        for row in Case.objects.values("risk_level").annotate(count=Count("id")):
            risk_counts[row["risk_level"]] += row["count"]
        for score in Applicant.objects.values_list("fraud_score", flat=True):
            risk_counts[_risk_from_score(score)] += 1
        for row in AnalyticsCase.objects.values("risk_level").annotate(count=Count("id")):
            risk_counts[row["risk_level"]] += row["count"]

        risk_data = [
            {"risk_level": risk_level, "count": count}
            for risk_level, count in risk_counts.items()
        ]

        buckets = {
            "0-20": 0,
            "21-40": 0,
            "41-60": 0,
            "61-80": 0,
            "81-100": 0,
        }

        for score in Case.objects.values_list("fraud_score", flat=True):
            if score is None:
                continue
            score_value = float(score)
            if score_value <= 20:
                buckets["0-20"] += 1
            elif score_value <= 40:
                buckets["21-40"] += 1
            elif score_value <= 60:
                buckets["41-60"] += 1
            elif score_value <= 80:
                buckets["61-80"] += 1
            else:
                buckets["81-100"] += 1

        for score in Applicant.objects.values_list("fraud_score", flat=True):
            if score is None:
                continue
            score_value = float(score)
            if score_value <= 20:
                buckets["0-20"] += 1
            elif score_value <= 40:
                buckets["21-40"] += 1
            elif score_value <= 60:
                buckets["41-60"] += 1
            elif score_value <= 80:
                buckets["61-80"] += 1
            else:
                buckets["81-100"] += 1

        for prob in AnalyticsCase.objects.values_list("fraud_probability", flat=True):
            if prob is None:
                continue
            score_value = float(prob) * 100
            if score_value <= 20:
                buckets["0-20"] += 1
            elif score_value <= 40:
                buckets["21-40"] += 1
            elif score_value <= 60:
                buckets["41-60"] += 1
            elif score_value <= 80:
                buckets["61-80"] += 1
            else:
                buckets["81-100"] += 1

        synthetic_by_date = defaultdict(int)
        for row in Case.objects.filter(
            synthetic_status="SUSPECT",
            created_at__gte=last_7_days
        ).extra({'day': "date(created_at)"}).values("day").annotate(count=Count("id")):
            synthetic_by_date[str(row["day"])] += row["count"]
        for row in AnalyticsCase.objects.filter(
            is_synthetic_id=True,
            created_at__gte=last_7_days
        ).extra({'day': "date(created_at)"}).values("day").annotate(count=Count("id")):
            synthetic_by_date[str(row["day"])] += row["count"]
        synthetic_week = [
            {"day": day, "count": count}
            for day, count in sorted(synthetic_by_date.items())
        ]

        aml_by_date = defaultdict(int)
        for row in Case.objects.filter(
            aml_status="SANCTION_HIT",
            created_at__gte=last_7_days
        ).extra({'day': "date(created_at)"}).values("day").annotate(count=Count("id")):
            aml_by_date[str(row["day"])] += row["count"]
        for row in AnalyticsCase.objects.filter(
            is_aml_hit=True,
            created_at__gte=last_7_days
        ).extra({'day': "date(created_at)"}).values("day").annotate(count=Count("id")):
            aml_by_date[str(row["day"])] += row["count"]
        for row in Applicant.objects.filter(
            aml_status="HIT",
            created_at__gte=last_7_days
        ).extra({'day': "date(created_at)"}).values("day").annotate(count=Count("id")):
            aml_by_date[str(row["day"])] += row["count"]
        aml_week = [
            {"day": day, "count": count}
            for day, count in sorted(aml_by_date.items())
        ]

        # New Metrics
        case_scores = [float(s) for s in Case.objects.values_list("fraud_score", flat=True) if s is not None]
        applicant_scores = [float(s) for s in Applicant.objects.values_list("fraud_score", flat=True) if s is not None]
        analytics_scores = [float(p) * 100 for p in AnalyticsCase.objects.values_list("fraud_probability", flat=True) if p is not None]
        
        all_scores = [*case_scores, *applicant_scores, *analytics_scores]
        avg_score = (sum(all_scores) / len(all_scores)) if all_scores else 0
        behavioral_flags = Case.objects.exclude(behavioral_risk="LOW").count()
        pattern_matches = Case.objects.exclude(pattern_match="NO MATCH").count()

        # High Risk Applicants (Top 5)
        high_risk_rows = []

        for row in Case.objects.all().values(
            "case_id", "name", "fraud_score", "aml_status", "status", "created_at"
        ):
            high_risk_rows.append({
                "id": row["case_id"],
                "name": row["name"],
                "score": row["fraud_score"],
                "aml": _normalize_aml(row["aml_status"]),
                "status": row["status"],
                "created_at": row["created_at"],
            })

        for row in Applicant.objects.all().values(
            "case_id", "name", "fraud_score", "aml_status", "status", "created_at"
        ):
            high_risk_rows.append({
                "id": row["case_id"],
                "name": row["name"],
                "score": row["fraud_score"],
                "aml": _normalize_aml(row["aml_status"]),
                "status": row["status"],
                "created_at": row["created_at"],
            })

        for row in AnalyticsCase.objects.all().values(
            "id", "customer_name", "fraud_probability", "is_aml_hit", "created_at", "risk_level"
        ):
            high_risk_rows.append({
                "id": f"AC-{row['id']}",
                "name": row["customer_name"],
                "score": int((row["fraud_probability"] or 0) * 100),
                "aml": "HIT" if row["is_aml_hit"] else "CLEAR",
                "status": row["risk_level"] or "PREDICTED",
                "created_at": row["created_at"],
            })

        deduped_high_risk_rows = {}
        for row in high_risk_rows:
            existing = deduped_high_risk_rows.get(row["id"])
            if not existing or row["created_at"] > existing["created_at"]:
                deduped_high_risk_rows[row["id"]] = row

        high_risk_rows = sorted(
            deduped_high_risk_rows.values(),
            key=lambda item: item["created_at"],
            reverse=True,
        )[:5]
        high_risk_applicants = [
            {
                "id": row["id"],
                "name": row["name"],
                "score": f"{row['score']}%",
                "aml": row["aml"],
                "status": row["status"],
            }
            for row in high_risk_rows
        ]

        # Recent Alerts (Top 10)
        recent_alerts_list = Alert.objects.all().order_by('-created_at')[:10]
        formatted_alerts = []
        for a in recent_alerts_list:
            formatted_alerts.append({
                "type": a.get_alert_type_display(),
                "detail": a.message,
                "time": a.created_at.strftime("%I:%M %p")
            })

        return Response({
            # Original Dashboard keys (snake_case)
            "risk_distribution": list(risk_data),
            "synthetic_weekly": list(synthetic_week),
            "aml_weekly": list(aml_week),
            "fraud_score_buckets": buckets,
            "avg_fraud_score": round(avg_score, 1),
            "behavioral_flags": behavioral_flags,
            "pattern_matches": pattern_matches,
            "highRiskApplicants": high_risk_applicants,
            "alerts": formatted_alerts,
            
            # New Analytics keys (camelCase for Analytics.jsx)
            "fraudScoreDistribution": [{"bucket": k, "count": v} for k, v in buckets.items()],
            "riskCategoryPie": [{"name": r["risk_level"], "value": r["count"]} for r in risk_data],
            "syntheticAlertsTrend": [{"date": str(r["day"]), "count": r["count"]} for r in synthetic_week],
            "amlTrend": [{"date": str(r["day"]), "count": r["count"]} for r in aml_week]
        })

