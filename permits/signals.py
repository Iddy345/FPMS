from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Requisition, Coupon, User
import threading

def send_async_email(subject, message, recipients):
    if not recipients:
        return
    threading.Thread(target=send_mail, args=(
        subject, message, settings.DEFAULT_FROM_EMAIL or 'no-reply@fuel.com',
        recipients, False
    )).start()

@receiver(post_save, sender=Requisition)
def requisition_signals(sender, instance, created, **kwargs):
    req = instance
    driver_email = [req.driver.email] if req.driver.email else []

    if created and req.driver.department:
        hods = User.objects.filter(role='hod', department=req.driver.department)
        hod_emails = [h.email for h in hods if h.email]
        if hod_emails:
            send_async_email("New Fuel Requisition", f"Driver {req.driver.username} submitted #{req.id}", hod_emails)

    elif hasattr(req, '_old_status') and req._old_status != req.status:
        if req.status == 'rejected' and driver_email:
            send_async_email("Requisition Rejected", f"Request #{req.id} rejected.\nReason: {req.rejection_reason or 'N/A'}", driver_email)
        elif req.status == 'approved_hod':
            emails = [u.email for u in User.objects.filter(role='transport') if u.email]
            send_async_email("Ready for Transport Review", f"Requisition #{req.id} approved by HOD", emails)
        elif req.status == 'approved_transport':
            emails = [u.email for u in User.objects.filter(role='pmu') if u.email]
            send_async_email("Ready for PMU Review", f"Requisition #{req.id} approved by Transport", emails)
        elif req.status == 'approved_finance' and driver_email:
            send_async_email("Coupon Issued!", f"Your coupon for #{req.id} is ready!", driver_email)

@receiver(post_save, sender=Coupon)
def coupon_signal(sender, instance, created, **kwargs):
    if created:
        emails = [u.email for u in User.objects.filter(role='finance') if u.email]
        send_async_email("New Coupon Generated", f"Coupon {instance.coupon_code} for Req #{instance.requisition.id}", emails)