from django.db import models
from django.utils.translation import gettext_lazy as _

class PlanTypeEnum(models.TextChoices):
    FREEMIUM = "freemium", _("Freemium")
    CRECE = "crece", _("Crece")
    PRO_PLUS = "pro+", _("Pro+")
    EMPRESA = "empresa", _("Empresa")

class Payment(models.Model):
    STATUS_CHOICES = (
        ("completed", "Completed"),
        ("pending", "Pending"),
        ("failed", "Failed"),
    )
    plan_type = models.CharField(max_length=20, choices=PlanTypeEnum.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField()
    end_date = models.DateTimeField()
    transaction_id = models.CharField(max_length=100, blank=True)
    discount_applied_for_weeks = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    currency = models.CharField(max_length=3, default="PEN")
    yape_image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Payment {self.id} - {self.plan_type}"

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="PEN")
    duration_days = models.IntegerField()
    features = models.JSONField(default=list)
    plan_type = models.CharField(max_length=20, choices=PlanTypeEnum.choices)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    discount_end_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

class PlanDefinition(models.Model):
    name = models.CharField(max_length=100)
    weekly_cost = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.JSONField(default=list)
    plan_type = models.CharField(max_length=20, choices=PlanTypeEnum.choices, unique=True)

    def __str__(self):
        return self.name