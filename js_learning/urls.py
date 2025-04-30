from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from courses import views
from js_learning import settings
from django.contrib.auth import get_user_model
User = get_user_model()
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('courses.urls')),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:lesson_id>/test/', views.test_view, name='test_view'),
    path('test/<int:test_id>/submit/', views.submit_test, name='submit_test'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)