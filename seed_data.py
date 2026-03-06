import random
from datetime import timedelta
from django.utils import timezone
from cases.models import Case, AuditTrail
from dashboard.models import Applicant, Alert
from django.contrib.auth import get_user_model

User = get_user_model()
admin_user = User.objects.filter(is_superuser=True).first() or User.objects.first()

# 1. Clear existing data (optional but cleaner for demo)
Case.objects.all().delete()
Applicant.objects.all().delete()
Alert.objects.all().delete()

names = [
    "Ravi Sharma", "Ananya Iyer", "Siddharth Goel", "Mehak Kapoor", "Vikram Rathore",
    "Priya Deshmukh", "Sameer Verma", "Aarav Gupta", "Nisha Reddy", "Arjun Mehra",
    "Sneha Patil", "Rohan Joshi", "Ishita Chawla", "Karan Malhotra", "Riya Singh",
    "Aditya Saxena", "Tanya Bhatia", "Aaryan Khan", "Divya Pillai", "Rahul Oberoi"
]

risks = ["HIGH", "MEDIUM", "LOW"]
statuses = ["REVIEW", "UNDERWRITING", "APPROVED", "REJECTED", "BLACKLISTED"]
shits = ["CLEAR", "SANCTION_HIT"]
synths = ["CLEAN", "SUSPECT"]

print("Seeding Cases and Applicants...")
for i in range(20):
    case_id = f"CASE-{1000 + i}"
    name = random.choice(names)
    f_score = random.randint(10, 95)
    
    # Matching Case Model
    case = Case.objects.create(
        case_id=case_id,
        name=name,
        mobile=f"9876543{random.randint(100, 999)}",
        pan=f"ABCDE{random.randint(1000, 9999)}F",
        status=random.choice(statuses),
        fraud_score=f_score,
        synthetic_status=random.choice(synths),
        aml_status=random.choice(shits),
        behavioral_risk="HIGH" if f_score > 80 else "LOW",
        pattern_match="NO MATCH" if f_score < 70 else "MULTIPLE DEVICES",
        eligibility_done=True,
        kyc_done=random.choice([True, False]),
        fraud_check_done=True if f_score > 0 else False,
    )
    
    # Matching Dashboard Applicant Model
    Applicant.objects.create(
        case_id=case_id,
        name=name,
        fraud_score=f_score,
        aml_status="HIT" if case.aml_status == "SANCTION_HIT" else "CLEAR",
        status="APPROVED" if case.status == "APPROVED" else "REVIEW",
    )
    
    # Audit trail
    AuditTrail.objects.create(
        case=case,
        action="Case Created",
        performed_by=admin_user,
        timestamp=timezone.now() - timedelta(hours=random.randint(1, 48))
    )

print("Seeding Alerts...")
alert_types = [
    ('AML_MATCH', 'Multiple identity matches found in OFAC list'),
    ('HIGH_FRAUD', 'Fraud score exceeded threshold (>80)'),
    ('DOC_MISMATCH', 'ID photo does not match liveness selfie')
]

for _ in range(10):
    a_type, msg = random.choice(alert_types)
    Alert.objects.create(
        alert_type=a_type,
        message=msg
    )

print("Seeding Complete!")
