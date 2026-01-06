from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Requisition, LogBook, Coupon

class UserRegistrationForm(UserCreationForm):
    department = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'department')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'driver'
        if commit:
            user.save()
        return user

class RequisitionForm(forms.ModelForm):
    class Meta:
        model = Requisition
        fields = ('fuel_amount', 'purpose')

class LogBookForm(forms.ModelForm):
    class Meta:
        model = LogBook
        fields = ('entry_date', 'mileage_start', 'mileage_end', 'fuel_used', 'notes')

class RejectionForm(forms.Form):
    rejection_reason = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}))

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ('coupon_code', 'cost')