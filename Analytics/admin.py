from django.contrib import admin
from .models import Case


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):

    list_display = (
        "customer_name",
        "risk_level",
        "fraud_probability",
        "is_synthetic_id",
        "is_aml_hit",
        "created_at",
    )

    list_filter = (
        "risk_level",
        "is_synthetic_id",
        "is_aml_hit",
        "created_at",
    )

    search_fields = ("customer_name",)
    ordering = ("-created_at",)