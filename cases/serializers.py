from rest_framework import serializers
from .models import Case, AuditTrail


class AuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditTrail
        fields = ["id", "action", "timestamp"]


class CaseSerializer(serializers.ModelSerializer):
    risk_level = serializers.SerializerMethodField()
    audits = AuditSerializer(many=True, read_only=True)

    class Meta:
        model = Case
        fields = "__all__"

    def get_risk_level(self, obj):
        return obj.risk_level()

