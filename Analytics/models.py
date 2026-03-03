from django.db import models


class Case(models.Model):

    RISK_CHOICES = [
        ("LOW", "Low Risk"),
        ("MEDIUM", "Medium Risk"),
        ("HIGH", "High Risk"),
    ]

    customer_name = models.CharField(max_length=255)

    transaction_amount = models.FloatField()
    transaction_count = models.IntegerField()
    device_risk_score = models.FloatField()
    location_risk_score = models.FloatField()

    fraud_probability = models.FloatField(null=True, blank=True)
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES)

    is_synthetic_id = models.BooleanField(default=False)
    is_aml_hit = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.risk_level}"