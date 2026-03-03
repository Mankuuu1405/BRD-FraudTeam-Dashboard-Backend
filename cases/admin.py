# from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Investigation
from django.contrib import admin
from django.utils.html import format_html
from .models import Case, AuditTrail



@admin.register(Investigation)
class InvestigationAdmin(admin.ModelAdmin):
    list_display = ['investigation_id', 'applicant_name', 'fraud_score', 'aml_status', 'synthetic_id_status', 'updated_at']
    search_fields = ['investigation_id', 'applicant_name']
    list_filter = ['aml_status', 'synthetic_id_status', 'risk_level']
    ordering = ['-updated_at']

# 🔹 Inline Audit Trail (inside Case page)
class AuditTrailInline(admin.TabularInline):
    model = AuditTrail
    extra = 0
    readonly_fields = ("action", "performed_by", "timestamp")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):

    list_display = (
        "case_id",
        "name",
        "mobile",
        "pan",
        "colored_status",
        "fraud_score",
        "aml_status",
        "synthetic_status",
        "created_at",
    )

    list_filter = (
        "status",
        "aml_status",
        "synthetic_status",
        "behavioral_risk",
        "pattern_match",
        "created_at",
    )

    search_fields = ("case_id", "name", "mobile", "pan")

    readonly_fields = (
        "created_at",
        "face_match_display",
        "liveness_display",
        "income_confidence_display",
        "cibil_score_display",
        "is_blacklisted_display",
        "hash_verified_display",
    )

    inlines = [AuditTrailInline]

    # ─── Fieldsets ────────────────────────────────────────────────────────────
    fieldsets = (

    ("Basic Information", {
        "fields": (
            "case_id",
            "name",
            "mobile",
            "pan",
            "status",
            "created_at",
        )
    }),

    ("Progress Tracking", {
        "fields": (
            "eligibility_done",
            "kyc_done",
            "fraud_check_done",
            "aml_done",
            "underwriting_done",
            "document_execution_done",
            "disbursement_done",
        )
    }),

    ("Fraud Indicators", {
        "fields": (
            "fraud_score",
            "synthetic_status",
            "aml_status",
            "behavioral_risk",
            "pattern_match",
        )
    }),

    # ✅ KYC Section
    ("KYC Verification", {
        "fields": (
            "pan_match",
            "aadhaar_match",
        )
    }),

    # ✅ Biometrics Section
    ("Biometrics", {
        "fields": (
            "face_match_score",
            "liveness_display",
        )
    }),

    # ✅ Geo Location
    ("Geo Location", {
        "fields": (
            "negative_area",
        )
    }),

    # ✅ Financial Documents
    ("Financial Documents", {
        "fields": (
            "income_confidence_score",
        )
    }),

    # ✅ Bureau Check
    ("Bureau Check", {
        "fields": (
            "cibil_score",
            "is_blacklisted",
        )
    }),

    # ✅ Blockchain Identity
    ("Blockchain Identity Match", {
        "fields": (
            "hash_verified",
        )
    }),

)

    # ─── Colored Status Badge ───────────────────────────────────────────────
    def colored_status(self, obj):
        color = "gray"
        if obj.status == "APPROVED":
            color = "green"
        elif obj.status == "REJECTED":
            color = "red"
        elif obj.status == "UNDERWRITING":
            color = "blue"
        elif obj.status == "BLACKLISTED":
            color = "black"
        elif obj.status == "REVIEW":
            color = "orange"

        return format_html(
            '<span style="color: white; background-color: {}; padding: 4px 8px; border-radius: 6px;">{}</span>',
            color,
            obj.status
        )
    colored_status.short_description = "Status"

    # ─── Verification Display Methods ───────────────────────────────────────
    def face_match_display(self, obj):
        return f"{obj.face_match_score}%" if obj.face_match_score is not None else "-"
    face_match_display.short_description = "Face Match Score"

    def liveness_display(self, obj):
        return "Passed" if obj.liveness_passed else "Failed"
    liveness_display.short_description = "Liveness Check"

    def income_confidence_display(self, obj):
        return f"{obj.income_confidence_score}%" if obj.income_confidence_score is not None else "-"
    income_confidence_display.short_description = "Income Confidence Score"

    def cibil_score_display(self, obj):
        return obj.cibil_score or "-"
    cibil_score_display.short_description = "CIBIL Score"

    def is_blacklisted_display(self, obj):
        return "Yes" if obj.is_blacklisted else "No"
    is_blacklisted_display.short_description = "Blacklisted"

    def hash_verified_display(self, obj):
        return "Verified" if obj.hash_verified else "Not Verified"
    hash_verified_display.short_description = "Hash Match"


@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):

    list_display = ("case", "action", "performed_by", "timestamp")
    list_filter = ("performed_by", "timestamp")
    search_fields = ("case__case_id", "action")
    readonly_fields = ("case", "action", "performed_by", "timestamp")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False