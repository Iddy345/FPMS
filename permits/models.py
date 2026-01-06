from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save
from django.dispatch import receiver

class User(AbstractUser):
    ROLE_CHOICES = (
        ('driver', 'Driver'),
        ('hod', 'Head of Department'),
        ('transport', 'Transport Officer'),
        ('pmu', 'PMU Officer'),
        ('finance', 'Finance Officer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='driver')
    department = models.CharField(max_length=100, blank=True, null=True)

class Requisition(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
        ('approved_hod', 'Approved by HOD'),
        ('approved_transport', 'Approved by Transport'),
        ('approved_pmu', 'Approved by PMU'),
        ('approved_finance', 'Approved by Finance'),
    )
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requisitions')
    date_requested = models.DateTimeField(auto_now_add=True)
    fuel_amount = models.FloatField()
    purpose = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True)

class LogBook(models.Model):
    driver = models.ForeignKey(User, on_delete=models.CASCADE)
    entry_date = models.DateField()
    mileage_start = models.FloatField()
    mileage_end = models.FloatField()
    fuel_used = models.FloatField()
    notes = models.TextField(blank=True)

class Coupon(models.Model):
    requisition = models.OneToOneField(Requisition, on_delete=models.CASCADE)
    coupon_code = models.CharField(max_length=50, unique=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_generated = models.DateTimeField(auto_now_add=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2)

@receiver(pre_save, sender=Requisition)
def track_status(sender, instance, **kwargs):
    if instance.pk:
        instance._old_status = Requisition.objects.get(pk=instance.pk).status
    else:
        instance._old_status = None