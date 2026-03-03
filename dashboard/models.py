from django.db import models


from django.contrib.auth.models import User
from django.db import models
from django.conf import settings  # Important!

from django.db import models
from django.conf import settings

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Applicant(models.Model):
    AML_STATUS = [
        ('HIT', 'HIT'),
        ('CLEAR', 'CLEAR'),
    ]

    STATUS_CHOICES = [
        ('REVIEW', 'REVIEW'),
        ('PENDING', 'PENDING'),
        ('APPROVED', 'APPROVED'),
    ]

    case_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    fraud_score = models.IntegerField()
    aml_status = models.CharField(max_length=10, choices=AML_STATUS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.case_id} - {self.name}"


class Alert(models.Model):
    ALERT_TYPES = [
        ('AML_MATCH', 'AML Match'),
        ('HIGH_FRAUD', 'High Fraud Score'),
        ('DOC_MISMATCH', 'Document Mismatch'),
    ]

    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.alert_type


class DashboardMetric(models.Model):
    fraud_score = models.IntegerField(default=0)
    synthetic_id_alerts = models.IntegerField(default=0)
    aml_hits = models.IntegerField(default=0)
    behavioral_flags = models.IntegerField(default=0)
    pattern_matches = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Dashboard Metrics"

from django.db import models


class Case(models.Model):
    RISK_LEVEL_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]

    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES)
    fraud_probability = models.FloatField()
    is_synthetic_id = models.BooleanField(default=False)
    is_aml_hit = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.risk_level} - {self.fraud_probability}"