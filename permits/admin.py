from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import User, Requisition, LogBook, Coupon

admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email','first_name','last_name', 'role', 'department', 'is_staff','is_superuser')
    list_filter = ('role', 'department','is_staff','is_active')
    search_fields=('username','email','first_name','last_name')
    ordering=('username',)

    fieldsets =(
        (None,{'fields':('username','password')}),
        ('personal info', {'fields':('first_name','last_name','email')}),
        ('custom fields',{'fields': ('role','department')}),
        ('permissions',{'fields':('is_active','is_staff','is_superuser')}),
        ('Important dates', {'fields':('last_login','date_joined')}),
    )
    add_fieldsets =(
        (None, {
            'classes':('wide',),
            'fields':('username','email','password1','password2','role','department','is_staff','is_active')},
        ),
    )


admin.site.register(Requisition)
admin.site.register(LogBook)
admin.site.register(Coupon)