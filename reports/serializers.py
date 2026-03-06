from rest_framework import serializers
from .models import Report


class ReportRequestSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(choices=[
        ("FRAUD_SUMMARY", "Fraud Summary"),
        ("AML_SANCTION", "AML Sanction"),
        ("HIGH_RISK", "High Risk"),
        ("SYNTHETIC_ID", "Synthetic ID"),
        ("ALL_CASES", "All Case Records"),
    ])

    start_date = serializers.DateField()
    end_date = serializers.DateField()


class ReportHistorySerializer(serializers.ModelSerializer):
    generated_by_email = serializers.EmailField(source="generated_by.email", read_only=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "report_type",
            "start_date",
            "end_date",
            "created_at",
            "generated_by_email",
        ]