from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from js_learning import settings
from django.contrib.auth import get_user_model
User = get_user_model()
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('courses.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)