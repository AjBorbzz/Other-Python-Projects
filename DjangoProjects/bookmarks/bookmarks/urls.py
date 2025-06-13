
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static # serve media files

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
]

if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    
# NOTE: Never use the static() helper function in Production. Django is very inefficient at serving static files.