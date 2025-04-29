from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(course, id=course_id)
    
    # Проверка доступа для студентов
    if request.user.is_student:
        if not course.is_active:
            raise PermissionDenied("Курс не доступен")
        # Дополнительные проверки для студентов при необходимости
    
    return render(request, 'courses/course_detail.html', {'course': course})
# Create your views here.
