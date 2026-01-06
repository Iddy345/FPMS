from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
import csv
from .forms import UserRegistrationForm, RequisitionForm, LogBookForm, RejectionForm, CouponForm
from .models import Requisition, LogBook, Coupon, User
from django.contrib.auth import logout as auth_logout
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome, Driver.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
         messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}

    if user.role == 'driver':
        last_week = timezone.now() - timedelta(weeks=1)
        context['requisitions'] = Requisition.objects.filter(driver=user, date_requested__gte=last_week)
        return render(request, 'driver_dashboard.html', context)

    elif user.role == 'hod':
        context['requisitions'] = Requisition.objects.filter(
            driver__department=user.department, status='pending'
        )
        return render(request, 'hod_dashboard.html', context)

    elif user.role == 'transport':
        context['requisitions'] = Requisition.objects.filter(status='approved_hod')
        return render(request, 'transport_dashboard.html', context)

    elif user.role == 'pmu':
        context['requisitions'] = Requisition.objects.filter(status='approved_transport')
        return render(request, 'pmu_dashboard.html', context)

    elif user.role == 'finance':
        context['requisitions'] = Requisition.objects.filter(status='approved_pmu')
        return render(request, 'finance_dashboard.html', context)

    return redirect('login')

@login_required
def request_permit(request):
    if request.user.role != 'driver':
        return redirect('dashboard')
    if request.method == 'POST':
        form = RequisitionForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.driver = request.user
            req.save()
            messages.success(request, 'Fuel requisition submitted successfully!')
            return redirect('dashboard')
    else:
        form = RequisitionForm()
    return render(request, 'request_permit.html', {'form': form})

@login_required
def view_requests(request):
    if request.user.role != 'driver':
        return redirect('dashboard')
    requisitions = Requisition.objects.filter(driver=request.user).order_by('-date_requested')
    return render(request, 'view_requests.html', {'requisitions': requisitions})

@login_required
def edit_requisition(request, req_id):
    req = get_object_or_404(Requisition, id=req_id, driver=request.user, status='rejected')
    if request.method == 'POST':
        form = RequisitionForm(request.POST, instance=req)
        if form.is_valid():
            form.save()
            req.status = 'pending'
            req.rejection_reason = ''
            req.save()
            messages.success(request, 'Request updated and resubmitted!')
            return redirect('view_requests')
    else:
        form = RequisitionForm(instance=req)
    return render(request, 'edit_requisition.html', {'form': form, 'req': req})

@login_required
def view_logbook(request):
    if request.user.role != 'driver':
        return redirect('dashboard')
    logbooks = LogBook.objects.filter(driver=request.user).order_by('-entry_date')
    return render(request, 'view_logbook.html', {'logbooks': logbooks})

@login_required
def add_logbook(request):
    if request.user.role != 'driver':
        return redirect('dashboard')
    if request.method == 'POST':
        form = LogBookForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.driver = request.user
            log.save()
            messages.success(request, 'Log book entry added!')
            return redirect('view_logbook')
    else:
        form = LogBookForm()
    return render(request, 'add_logbook.html', {'form': form})

@login_required
def view_requisition(request, req_id):
    req = get_object_or_404(Requisition, id=req_id)
    logbook = LogBook.objects.filter(driver=req.driver).order_by('-entry_date').first() if request.user.role in ['transport', 'pmu'] else None
    return render(request, 'view_requisition.html', {'req': req, 'logbook': logbook})

@login_required
def approve_reject(request, req_id, action, role):
    req = get_object_or_404(Requisition, id=req_id)
    if request.user.role != role:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    if request.method == 'POST':
        if action == 'reject':
            form = RejectionForm(request.POST)
            if form.is_valid():
                req.rejection_reason = form.cleaned_data['rejection_reason']
                req.status = 'rejected'
                req.save()
                messages.success(request, 'Requisition rejected.')
                return redirect('dashboard')
        elif action == 'approve':
            if role == 'hod':
                req.status = 'approved_hod'
            elif role == 'transport':
                req.status = 'approved_transport'
            elif role == 'pmu':
                req.status = 'approved_pmu'
                req.save()
                return redirect('generate_coupon', req_id=req.id)
            elif role == 'finance':
                req.status = 'approved_finance'
            req.save()
            messages.success(request, 'Requisition approved.')
            return redirect('dashboard')
    else:
        form = RejectionForm() if action == 'reject' else None

    return render(request, 'approve_reject.html', {'req': req, 'form': form, 'action': action})

@login_required
def generate_coupon(request, req_id):
    if request.user.role != 'pmu':
        return redirect('dashboard')
    req = get_object_or_404(Requisition, id=req_id, status='approved_pmu')
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            coupon = form.save(commit=False)
            coupon.requisition = req
            coupon.generated_by = request.user
            coupon.save()
            messages.success(request, f'Coupon {coupon.coupon_code} generated successfully!')
            return redirect('dashboard')
    else:
        form = CouponForm(initial={'coupon_code': f'CPN-{req.id}-{timezone.now().strftime("%Y%m%d")}'})
    return render(request, 'generate_coupon.html', {'form': form, 'req': req})

@login_required
def download_coupon(request, req_id):
    if request.user.role != 'driver':
        return redirect('dashboard')
    req = get_object_or_404(Requisition, id=req_id, driver=request.user, status='approved_finance')
    if not hasattr(req, 'coupon'):
        messages.error(request, 'Coupon not generated yet.')
        return redirect('view_requests')
    coupon = req.coupon
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="Coupon_{coupon.coupon_code}.txt"'
    content = f"""
FUEL COUPON
=============
Code: {coupon.coupon_code}
Driver: {req.driver.username}
Litres: {req.fuel_amount}
Purpose: {req.purpose}
Cost: {coupon.cost}
Issued On: {coupon.date_generated.strftime('%Y-%m-%d')}
Generated By: {coupon.generated_by.username if coupon.generated_by else 'PMU'}
    """
    response.write(content)
    return response

@login_required
def monthly_report(request):
    if request.user.role != 'finance':
        return redirect('dashboard')
    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    coupons = Coupon.objects.filter(date_generated__gte=start_of_month, requisition__status='approved_finance')
    total_liters = sum(c.requisition.fuel_amount for c in coupons)
    total_cost = sum(c.cost for c in coupons)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="Monthly_Report_{now.strftime("%B_%Y")}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Coupon Code', 'Driver', 'Litres', 'Cost', 'Date Generated'])
    for c in coupons:
        writer.writerow([c.coupon_code, c.requisition.driver.username, c.requisition.fuel_amount, c.cost, c.date_generated.strftime('%Y-%m-%d')])
    writer.writerow([])
    writer.writerow(['TOTAL', '', total_liters, total_cost, ''])
    return response

def home(request):
    return render(request, 'home.html')

def logout_view(request):
    auth_logout(request)
    messages.success(request, 'You Have Been Logged out Successfully.')
    return redirect('login')