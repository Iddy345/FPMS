from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('request_permit/', views.request_permit, name='request_permit'),
    path('view_requests/', views.view_requests, name='view_requests'),
    path('edit_requisition/<int:req_id>/', views.edit_requisition, name='edit_requisition'),
    path('view_logbook/', views.view_logbook, name='view_logbook'),
    path('add_logbook/', views.add_logbook, name='add_logbook'),
    path('view_requisition/<int:req_id>/', views.view_requisition, name='view_requisition'),
    path('approve_reject/<int:req_id>/<str:action>/<str:role>/', views.approve_reject, name='approve_reject'),
    path('generate_coupon/<int:req_id>/', views.generate_coupon, name='generate_coupon'),
    path('download_coupon/<int:req_id>/', views.download_coupon, name='download_coupon'),
    path('monthly_report/', views.monthly_report, name='monthly_report'),
    path('logout/', auth_views.LogoutView.as_view(),name='logout'),
    path('logout/', views.logout_view, name='logout')
]