from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from .models import Case
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

        from .ml_models import predict_fraud
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


from cases.models import Case as BusinessCase
from .models import Case as MLCase
# ----------------------------------
# DASHBOARD ANALYTICS
# ----------------------------------
class DashboardAnalyticsView(APIView):

    def get(self, request):
        # Time range for weekly trend
        today = timezone.now()

        # 1. RISK DISTRIBUTION (Aggregated from both models)
        # Business Cases
        biz_dist = BusinessCase.objects.values("risk_level").annotate(count=Count("id"))
        # ML Cases
        ml_dist = MLCase.objects.values("risk_level").annotate(count=Count("id"))
        
        # Combine
        dist_map = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for d in biz_dist:
            dist_map[d["risk_level"].upper()] = dist_map.get(d["risk_level"].upper(), 0) + d["count"]
        for d in ml_dist:
             dist_map[d["risk_level"].upper()] = dist_map.get(d["risk_level"].upper(), 0) + d["count"]
        
        risk_distribution = [{"risk_level": k, "count": v} for k, v in dist_map.items()]

        # 2. RISK SCORE RANGES (Aggregated)
        ranges = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
        
        # Ranges for ML Cases (0-1 probability)
        ranges["0-20"] += MLCase.objects.filter(fraud_probability__lt=0.2).count()
        ranges["21-40"] += MLCase.objects.filter(fraud_probability__gte=0.2, fraud_probability__lt=0.4).count()
        ranges["41-60"] += MLCase.objects.filter(fraud_probability__gte=0.4, fraud_probability__lt=0.6).count()
        ranges["61-80"] += MLCase.objects.filter(fraud_probability__gte=0.6, fraud_probability__lt=0.8).count()
        ranges["81-100"] += MLCase.objects.filter(fraud_probability__gte=0.8).count()
        
        # Ranges for Business Cases (0-100 score)
        ranges["0-20"] += BusinessCase.objects.filter(fraud_score__lt=20).count()
        ranges["21-40"] += BusinessCase.objects.filter(fraud_score__gte=20, fraud_score__lt=40).count()
        ranges["41-60"] += BusinessCase.objects.filter(fraud_score__gte=40, fraud_score__lt=60).count()
        ranges["61-80"] += BusinessCase.objects.filter(fraud_score__gte=60, fraud_score__lt=80).count()
        ranges["81-100"] += BusinessCase.objects.filter(fraud_score__gte=80).count()

        # 3. WEEKLY TREND (Aggregated from both models)
        synthetic_weekly_data = []
        aml_hits_weekly_data = []

        for i in range(4, -1, -1):
            target_date = (today - timedelta(days=i)).date()
            day_label = (today - timedelta(days=i)).strftime("%a")
            
            # Synthetic counts from both
            syn_biz = BusinessCase.objects.filter(created_at__date=target_date, synthetic_status="SUSPECT").count()
            syn_ml = MLCase.objects.filter(created_at__date=target_date, is_synthetic_id=True).count()
            synthetic_weekly_data.append({"name": day_label, "value": syn_biz + syn_ml})
            
            # AML hits from both
            aml_biz = BusinessCase.objects.filter(created_at__date=target_date, aml_status="SANCTION_HIT").count()
            aml_ml = MLCase.objects.filter(created_at__date=target_date, is_aml_hit=True).count()
            aml_hits_weekly_data.append({"name": day_label, "value": aml_biz + aml_ml})

        return Response({
            "risk_distribution": risk_distribution,
            "risk_score_distribution": ranges,
            "synthetic_id_weekly": synthetic_weekly_data,
            "aml_hits_weekly": aml_hits_weekly_data,
        })