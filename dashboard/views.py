from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Applicant, Alert, Case   # Make sure Case exists



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
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

    def get(self, request):

        last_7_days = timezone.now() - timedelta(days=7)

        # Risk Distribution
        risk_data = Case.objects.values("risk_level").annotate(count=Count("id"))

        # Weekly Synthetic ID
        synthetic_week = Case.objects.filter(
            is_synthetic_id=True,
            created_at__gte=last_7_days
        ).extra({
            'day': "date(created_at)"
        }).values("day").annotate(count=Count("id"))

        aml_week = Case.objects.filter(
            is_aml_hit=True,
            created_at__gte=last_7_days
        ).extra({
            'day': "date(created_at)"
        }).values("day").annotate(count=Count("id"))

        # Fraud Score Buckets
        buckets = {
            "0-20": Case.objects.filter(fraud_probability__lte=0.2).count(),
            "21-40": Case.objects.filter(fraud_probability__gt=0.2, fraud_probability__lte=0.4).count(),
            "41-60": Case.objects.filter(fraud_probability__gt=0.4, fraud_probability__lte=0.6).count(),
            "61-80": Case.objects.filter(fraud_probability__gt=0.6, fraud_probability__lte=0.8).count(),
            "81-100": Case.objects.filter(fraud_probability__gt=0.8).count(),
        }

        return Response({
            "risk_distribution": list(risk_data),
            "synthetic_weekly": list(synthetic_week),
            "aml_weekly": list(aml_week),
            "fraud_score_buckets": buckets
        })

