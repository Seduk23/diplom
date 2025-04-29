from django.contrib import admin
from .models import Course, Lesson, TestResult
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test  # Импорт декораторов
from django.shortcuts import render  # Импорт render

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'is_admin')
   

User = get_user_model()
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'lesson_count', 'student_count', 'is_active')
    
    def has_add_permission(self, request):
        return request.user.is_teacher or request.user.is_admin

    def has_change_permission(self, request, obj=None):
        if obj:
            return obj.creator == request.user or request.user.is_admin
        return True
    
    def lesson_count(self, obj):
        return obj.lessons.count()
    
    def student_count(self, obj):
        return TestResult.objects.filter(lesson__course=obj).values('student').distinct().count()

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'score', 'completed_at')
    list_filter = ('lesson__course', 'student')
    search_fields = ('student__username', 'lesson__title')

@admin.register(Lesson)  # Регистрируем Lesson отдельно
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course')
    list_filter = ('course',)
    
@login_required
@user_passes_test(lambda u: u.is_admin)
def admin_dashboard(request):
    courses = Course.objects.all()
    return render(request, 'courses/admin_dashboard.html', {'courses': courses})