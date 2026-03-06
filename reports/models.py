from django.db import models
from django.conf import settings


class Report(models.Model):

    REPORT_TYPES = [
        ("FRAUD_SUMMARY", "Fraud Summary"),
        ("AML_SANCTION", "AML Sanction"),
        ("HIGH_RISK", "High Risk"),
        ("SYNTHETIC_ID", "Synthetic ID"),
        ("ALL_CASES", "All Case Records"),
    ]

    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()

    # ✅ Correct way to reference custom user
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    file = models.FileField(upload_to="reports/", null=True, blank=True)

    def __str__(self):
        return f"{self.report_type} ({self.start_date} - {self.end_date})"