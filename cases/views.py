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

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Case, AuditTrail
from .serializers import CaseSerializer


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
            applicant_name=request.data.get("applicant_name"),
            fraud_score=fraud_score,
            risk_level=risk,
            aml_status=aml_status,
            synthetic_status=synthetic_status,
        )

        return Response(CaseSerializer(case).data, status=status.HTTP_201_CREATED)


class CaseListView(APIView):
    def get(self, request):
        cases = Case.objects.all().order_by("-created_at")
        serializer = CaseSerializer(cases, many=True)
        return Response(serializer.data)


class CaseDetailView(APIView):
    def get(self, request, case_id):
        case = get_object_or_404(Case, case_id=case_id)
        serializer = CaseSerializer(case)
        return Response(serializer.data)


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


