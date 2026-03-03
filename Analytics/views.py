from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from .models import Case
from .ml_model import predict_fraud


# ----------------------------------
# CREATE CASE (Fraud Prediction)
# ----------------------------------
class CreateCaseView(APIView):

    def post(self, request):

        data = request.data

        input_features = [
            float(data["transaction_amount"]),
            int(data["transaction_count"]),
            float(data["device_risk_score"]),
            float(data["location_risk_score"]),
        ]

        probability = predict_fraud(input_features)

        # Risk Classification
        if probability > 0.7:
            risk = "HIGH"
        elif probability > 0.4:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        case = Case.objects.create(
            customer_name=data["customer_name"],
            transaction_amount=input_features[0],
            transaction_count=input_features[1],
            device_risk_score=input_features[2],
            location_risk_score=input_features[3],
            fraud_probability=probability,
            risk_level=risk,
            is_synthetic_id=data.get("is_synthetic_id", False),
            is_aml_hit=data.get("is_aml_hit", False),
        )

        return Response({
            "message": "Case Created Successfully",
            "fraud_probability": round(probability, 3),
            "risk_level": risk,
        })


# ----------------------------------
# DASHBOARD ANALYTICS
# ----------------------------------
class DashboardAnalyticsView(APIView):

    def get(self, request):

        # Risk Distribution (Pie Chart)
        risk_distribution = Case.objects.values("risk_level").annotate(
            count=Count("id")
        )

        # Risk Score Distribution (Bar Chart)
        ranges = {
            "0-20": Case.objects.filter(fraud_probability__gte=0, fraud_probability__lt=0.2).count(),
            "21-40": Case.objects.filter(fraud_probability__gte=0.2, fraud_probability__lt=0.4).count(),
            "41-60": Case.objects.filter(fraud_probability__gte=0.4, fraud_probability__lt=0.6).count(),
            "61-80": Case.objects.filter(fraud_probability__gte=0.6, fraud_probability__lt=0.8).count(),
            "81-100": Case.objects.filter(fraud_probability__gte=0.8).count(),
        }

        # Weekly Data
        today = timezone.now()
        week_ago = today - timedelta(days=7)

        synthetic_weekly = Case.objects.filter(
            created_at__gte=week_ago,
            is_synthetic_id=True
        ).count()

        aml_weekly = Case.objects.filter(
            created_at__gte=week_ago,
            is_aml_hit=True
        ).count()

        return Response({
            "risk_distribution": list(risk_distribution),
            "risk_score_distribution": ranges,
            "synthetic_id_weekly": synthetic_weekly,
            "aml_hits_weekly": aml_weekly,
        })