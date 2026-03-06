from django.db import models
from django.utils import timezone

RISK_CHOICES = [
    ("HIGH", "High Risk"),
    ("MEDIUM", "Medium Risk"),
    ("LOW", "Low Risk"),
]

AML_STATUS = [
    ("CLEAR", "Clear"),
    ("SANCTION_HIT", "Sanction Hit"),
]

SYNTHETIC_STATUS = [
    ("CLEAN", "Clean"),
    ("SUSPECT", "Suspect"),
]

class Investigation(models.Model):
    investigation_id = models.CharField(max_length=30, unique=True)
    applicant_name = models.CharField(max_length=100)
    fraud_score = models.IntegerField(default=0)
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES, default="LOW")
    aml_status = models.CharField(max_length=20, choices=AML_STATUS, default="CLEAR")
    synthetic_id_status = models.CharField(max_length=20, choices=SYNTHETIC_STATUS, default="CLEAN")
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.investigation_id



from django.db import models
from django.conf import settings

class Case(models.Model):

    STATUS_CHOICES = [
        ("REVIEW", "Review"),
        ("UNDERWRITING", "Underwriting"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("BLACKLISTED", "Blacklisted"),
    ]

    case_id = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    pan = models.CharField(max_length=15)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="REVIEW")

    # Progress Steps
    eligibility_done = models.BooleanField(default=False)
    kyc_done = models.BooleanField(default=False)
    fraud_check_done = models.BooleanField(default=False)
    aml_done = models.BooleanField(default=False)
    underwriting_done = models.BooleanField(default=False)
    document_execution_done = models.BooleanField(default=False)
    disbursement_done = models.BooleanField(default=False)

    # Fraud Metrics
    fraud_score = models.IntegerField(default=0)
    risk_level = models.CharField(max_length=20, default="LOW")
    synthetic_status = models.CharField(max_length=20, default="CLEAR")
    aml_status = models.CharField(max_length=20, default="CLEAR")
    behavioral_risk = models.CharField(max_length=20, default="LOW")
    pattern_match = models.CharField(max_length=20, default="NO MATCH")

    created_at = models.DateTimeField(auto_now_add=True)

    # -------------------------
    # VERIFICATION SECTION
    # -------------------------

    # KYC
    pan_match = models.BooleanField(default=False)
    aadhaar_match = models.BooleanField(default=False)

    # Biometrics
    face_match_score = models.IntegerField(default=0)
    liveness_passed = models.BooleanField(default=False)


    negative_area = models.BooleanField(default=False)

    # Financial
    income_confidence_score = models.IntegerField(default=0)

    # Bureau
    cibil_score = models.IntegerField(default=0)
    is_blacklisted = models.BooleanField(default=False)

    # Blockchain
    hash_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.case_id


class AuditTrail(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="audits")
    action = models.CharField(max_length=255)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.case.case_id} - {self.action}"
