from django.contrib import admin
from .models import Course, Lesson, TestResult

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

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