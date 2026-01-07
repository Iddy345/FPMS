from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

# Import your custom views if needed
# from permits import views as permits_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # App-specific URLs (your main app: permits)
    path('', include('permits.urls')),  

    # Custom Logout - redirects to login page after logout
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)