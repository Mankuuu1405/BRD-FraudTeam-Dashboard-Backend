# from rest_framework import viewsets
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from .models import Case, AuditTrail
# from .serializers import CaseSerializer


# class CaseViewSet(viewsets.ModelViewSet):

#     queryset = Case.objects.all().order_by("-updated_at")
#     serializer_class = CaseSerializer

#     # 🔴 High Risk
#     @action(detail=False, methods=["get"])
#     def high_risk(self, request):
#         cases = Case.objects.filter(fraud_score__gte=80)
#         serializer = self.get_serializer(cases, many=True)
#         return Response(serializer.data)

#     # 🟡 Medium Risk
#     @action(detail=False, methods=["get"])
#     def medium_risk(self, request):
#         cases = Case.objects.filter(fraud_score__gte=50, fraud_score__lt=80)
#         serializer = self.get_serializer(cases, many=True)
#         return Response(serializer.data)

#     # 🟢 Low Risk
#     @action(detail=False, methods=["get"])
#     def low_risk(self, request):
#         cases = Case.objects.filter(fraud_score__lt=50)
#         serializer = self.get_serializer(cases, many=True)
#         return Response(serializer.data)

#     # 🚨 Sanction Hits
#     @action(detail=False, methods=["get"])
#     def sanction_hits(self, request):
#         cases = Case.objects.filter(aml_status="SANCTION_HIT")
#         serializer = self.get_serializer(cases, many=True)
#         return Response(serializer.data)

#     # 🧬 Synthetic Suspects
#     @action(detail=False, methods=["get"])
#     def synthetic_suspects(self, request):
#         cases = Case.objects.filter(synthetic_id_status="SUSPECT")
#         serializer = self.get_serializer(cases, many=True)
#         return Response(serializer.data)

#     # ✅ Approve
#     @action(detail=True, methods=["post"])
#     def approve(self, request, pk=None):
#         case = self.get_object()
#         case.status = "APPROVED"
# #         case.save()

# #         AuditTrail.objects.create(case=case, action="Case Approved")
# #         return Response({"message": "Case Approved"})

# #     # 🔵 Underwriting
# #     @action(detail=True, methods=["post"])
# #     def underwriting(self, request, pk=None):
# #         case = self.get_object()
# #         case.status = "UNDERWRITING"
# #         case.save()

# #         AuditTrail.objects.create(case=case, action="Moved to Underwriting")
# #         return Response({"message": "Underwriting Started"})

# #     # 🟠 Reject
# #     @action(detail=True, methods=["post"])
# #     def reject(self, request, pk=None):
# #         case = self.get_object()
# #         case.status = "REJECTED"
# #         case.save()

# #         AuditTrail.objects.create(case=case, action="Case Rejected")
# #         return Response({"message": "Case Rejected"})

# #     # 🔴 Blacklist
# #     @action(detail=True, methods=["post"])
# #     def blacklist(self, request, pk=None):
# #         case = self.get_object()
# #         case.status = "BLACKLISTED"
# #         case.save()

# #         AuditTrail.objects.create(case=case, action="Case Blacklisted")
# #         return Response({"message": "Case Blacklisted"})

# # ==========================================
# # DJANGO + DRF IMPORTS
# # ==========================================
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Case, AuditTrail
from .serializers import CaseSerializer
from Analytics.models import Case as AnalyticsCase


# ==========================================
# API VIEWS
# ==========================================

class CreateCaseView(APIView):
    def post(self, request):
        fraud_score = float(request.data.get("fraud_score", 0))

        if fraud_score > 70:
            risk = "HIGH"
        elif fraud_score > 40:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        aml_status = "SANCTION_HIT" if request.data.get("aml_status") == "SANCTION_HIT" else "CLEAR"
        synthetic_status = "SUSPECT" if request.data.get("synthetic_status") == "SUSPECT" else "CLEAN"

        case = Case.objects.create(
            case_id=request.data.get("case_id"),
            name=request.data.get("applicant_name") or request.data.get("name"),
            fraud_score=fraud_score,
            risk_level=risk,
            aml_status=aml_status,
            synthetic_status=synthetic_status,
        )

        return Response(CaseSerializer(case).data, status=status.HTTP_201_CREATED)


class CaseListView(APIView):
    def get(self, request):
        case_list = []
        
        # cases.models.Case
        cases = Case.objects.all().order_by("-created_at")
        for c in cases:
            case_list.append({
                "id": c.case_id,
                "name": c.name,
                "fraudScore": c.fraud_score,
                "aml": c.aml_status,
                "synthetic": c.synthetic_status,
                "updated": c.created_at.strftime("%Y-%m-%d %H:%M"),
                "status": c.status
            })
            
        # Analytics.models.Case
        analytics_cases = AnalyticsCase.objects.all().order_by("-created_at")
        for ac in analytics_cases:
            case_list.append({
                "id": f"AC-{ac.id}",
                "name": ac.customer_name,
                "fraudScore": int((ac.fraud_probability or 0) * 100),
                "aml": "HIT" if ac.is_aml_hit else "CLEAR",
                "synthetic": "SUSPECT" if ac.is_synthetic_id else "CLEAN",
                "updated": ac.created_at.strftime("%Y-%m-%d %H:%M"),
                "status": ac.risk_level or "PREDICTED"
            })
            
        return Response(case_list)


class CaseDetailView(APIView):
    def get(self, request, case_id):
        if str(case_id).startswith("AC-"):
            pk = case_id.replace("AC-", "")
            ac = get_object_or_404(AnalyticsCase, id=pk)
            # Create a duck-typed response for CaseDetails.jsx
            return Response({
                "id": case_id,
                "name": ac.customer_name,
                "fraudScore": int((ac.fraud_probability or 0) * 100),
                "aml": "HIT" if ac.is_aml_hit else "CLEAR",
                "synthetic": "SUSPECT" if ac.is_synthetic_id else "CLEAN",
                "updated": ac.created_at.strftime("%Y-%m-%d %H:%M"),
                "status": ac.risk_level or "PREDICTED",
                "applicant": {
                    "name": ac.customer_name,
                    "mobile": "N/A",
                    "pan": "N/A"
                },
                "workflow": {"status": ac.risk_level or "PREDICTED"},
                "fraudEngine": {
                    "fraudScore": int((ac.fraud_probability or 0) * 100),
                    "syntheticId": "SUSPECT" if ac.is_synthetic_id else "CLEAN",
                    "aml": "HIT" if ac.is_aml_hit else "CLEAR",
                    "behavioral": "LOW",
                    "pattern": "NO MATCH"
                },
                "verifications": {
                    "kyc": {"panMatch": False, "aadhaarMatch": False},
                    "biometrics": {"faceMatch": 0, "liveness": False},
                    "geo": {"negativeArea": False},
                    "financial": {"incomeConfidence": 0},
                    "bureau": {"cibil": 0, "blacklist": False},
                    "blockchain": {"identityHashMatch": False},
                },
                "audit": [],
                "progressStage": 1
            })
        
        case = get_object_or_404(Case, case_id=case_id)
        serializer = CaseSerializer(case)
        return Response(serializer.data)


class UpdateCaseStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    ACTION_TO_STATUS = {
        "approve": "APPROVED",
        "underwriting": "UNDERWRITING",
        "reject": "REJECTED",
        "blacklist": "BLACKLISTED",
    }

    def patch(self, request, case_id, action):
        case = get_object_or_404(Case, case_id=case_id)
        normalized_action = (action or "").lower()

        next_status = self.ACTION_TO_STATUS.get(normalized_action)
        if not next_status:
            return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        case.status = next_status
        if next_status == "UNDERWRITING":
            case.underwriting_done = True
        if next_status == "BLACKLISTED":
            case.is_blacklisted = True
        case.save()

        AuditTrail.objects.create(
            case=case,
            action=f"Case marked as {case.status}",
            performed_by=request.user,
        )

        return Response(CaseSerializer(case).data, status=status.HTTP_200_OK)


# ==========================================
# TEMPLATE VIEWS (HTML Dashboard)
# ==========================================

@login_required
def case_detail(request, case_id):
    case = get_object_or_404(Case, case_id=case_id)
    audits = case.audits.all().order_by("-timestamp")

    return render(request, "core/case_detail.html", {
        "case": case,
        "audits": audits,
    })


@login_required
def update_case_status(request, case_id, action):
    case = get_object_or_404(Case, case_id=case_id)

    if action == "approve":
        case.status = "APPROVED"
    elif action == "underwriting":
        case.status = "UNDERWRITING"
        case.underwriting_done = True
    elif action == "reject":
        case.status = "REJECTED"
    elif action == "blacklist":
        case.status = "BLACKLISTED"

    case.save()

    AuditTrail.objects.create(
        case=case,
        action=f"Case marked as {case.status}",
        performed_by=request.user
    )

    messages.success(request, f"Case updated to {case.status}")

    return redirect("case_detail", case_id=case.case_id)


