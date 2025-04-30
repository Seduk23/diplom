from django.urls import path
from courses.decorators import teacher_required
from js_learning import settings
from . import views
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.contrib.auth import get_user_model
User = get_user_model()
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='courses/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('signup/student/', views.student_signup, name='student_signup'),
    path('signup/teacher/', views.teacher_signup, name='teacher_signup'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    # Защищенные URL для преподавателей
    path('course/create/', teacher_required(views.create_course), name='create_course'),
    path('course/<int:course_id>/edit/', teacher_required(views.edit_course), name='edit_course'),
    path('course/<int:course_id>/lessons/', teacher_required(views.manage_lessons), name='manage_lessons'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)