from rest_framework import serializers
from .models import Case, AuditTrail


class AuditSerializer(serializers.ModelSerializer):
    ts = serializers.DateTimeField(source="timestamp", format="%Y-%m-%d %H:%M:%S")
    
    class Meta:
        model = AuditTrail
        fields = ["id", "action", "ts"]


class CaseSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="case_id", read_only=True)
    fraudScore = serializers.IntegerField(source="fraud_score")
    aml = serializers.CharField(source="aml_status")
    synthetic = serializers.CharField(source="synthetic_status")
    updated = serializers.DateTimeField(source="created_at", format="%Y-%m-%d %H:%M")
    
    # Detail fields (nested for CaseDetails.jsx)
    applicant = serializers.SerializerMethodField()
    workflow = serializers.SerializerMethodField()
    fraudEngine = serializers.SerializerMethodField()
    verifications = serializers.SerializerMethodField()
    audit = AuditSerializer(source="audits", many=True, read_only=True)
    progressStage = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = [
            "id", "name", "fraudScore", "aml", "synthetic", "updated", "status",
            "applicant", "workflow", "fraudEngine", "verifications", "audit", "progressStage"
        ]

    def get_progressStage(self, obj):
        # Calculate progress as an integer 0-7
        stages = [
            obj.eligibility_done,
            obj.kyc_done,
            obj.fraud_check_done,
            obj.aml_done,
            obj.underwriting_done,
            obj.document_execution_done,
            obj.disbursement_done
        ]
        count = 0
        for s in stages:
            if s: count += 1
            else: break
        return count

    def get_applicant(self, obj):
        return {
            "name": obj.name,
            "mobile": obj.mobile,
            "pan": obj.pan
        }

    def get_workflow(self, obj):
        return {
            "status": obj.status
        }

    def get_fraudEngine(self, obj):
        return {
            "fraudScore": obj.fraud_score,
            "syntheticId": obj.synthetic_status,
            "aml": obj.aml_status,
            "behavioral": obj.behavioral_risk,
            "pattern": obj.pattern_match
        }

    def get_verifications(self, obj):
        return {
            "kyc": {
                "panMatch": obj.pan_match,
                "aadhaarMatch": obj.aadhaar_match,
            },
            "biometrics": {
                "faceMatch": obj.face_match_score,
                "liveness": obj.liveness_passed,
            },
            "geo": {
                "negativeArea": obj.negative_area,
            },
            "financial": {
                "incomeConfidence": (obj.income_confidence_score or 0) / 100,
            },
            "bureau": {
                "cibil": obj.cibil_score,
                "blacklist": obj.is_blacklisted,
            },
            "blockchain": {
                "identityHashMatch": obj.hash_verified,
            },
        }

