from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
User = get_user_model()
def teacher_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_teacher:
            messages.error(request, 'Доступ только для преподавателей')
            return redirect('student_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper