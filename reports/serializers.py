from rest_framework import serializers
class ReportRequestSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(choices=[
        ("FRAUD_SUMMARY", "Fraud Summary"),
        ("AML_SANCTION", "AML Sanction"),
        ("HIGH_RISK", "High Risk"),
        ("SYNTHETIC_ID", "Synthetic ID"),
    ])

    start_date = serializers.DateField()
    end_date = serializers.DateField()