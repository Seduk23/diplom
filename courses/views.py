from django.shortcuts import render, get_object_or_404
from .models import Course, Lesson, Question, TestResult
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import LessonForm, StudentSignUpForm, TeacherSignUpForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CourseForm
from django.contrib.auth.decorators import user_passes_test
from .forms import StudentSignUpForm, TeacherSignUpForm, CourseForm, LessonForm, TestForm
from .decorators import teacher_required
from django.contrib.auth import get_user_model

User = get_user_model()
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all().order_by('order')
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'lessons': lessons
    })
def home(request):
    courses = Course.objects.all()  # Получаем все курсы из базы
    return render(request, 'courses/home.html', {'courses': courses})

def teacher_required(view_func):
    """Декоратор для проверки, что пользователь - преподаватель"""
    return user_passes_test(lambda u: u.is_teacher, login_url='student_dashboard')(view_func)

def student_required(view_func):
    """Декоратор для проверки, что пользователь - студент"""
    return user_passes_test(lambda u: u.is_student, login_url='teacher_dashboard')(view_func)

def student_signup(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('student_dashboard')
    else:
        form = StudentSignUpForm()
    return render(request, 'courses/student_signup.html', {'form': form})

def teacher_signup(request):
    if request.method == 'POST':
        form = TeacherSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # Перенаправляем на страницу создания первого курса
            messages.success(request, 'Регистрация прошла успешно! Создайте свой первый курс.')
            return redirect('create_course')
    else:
        form = TeacherSignUpForm()
    return render(request, 'courses/teacher_signup.html', {'form': form})

@login_required
def student_dashboard(request):
    courses = Course.objects.filter(is_active=True)
    progress = {}
    
    for course in courses:
        completed = TestResult.objects.filter(
            student=request.user,
            lesson__course=course
        ).values_list('lesson_id', flat=True).distinct().count()
        total = course.lessons.count()
        progress[course.id] = {
            'completed': completed,
            'total': total,
            'percent': int((completed / total) * 100) if total > 0 else 0
        }
    
    return render(request, 'courses/student_dashboard.html', {
        'courses': courses,
        'progress': progress
    })

@login_required
def admin_dashboard(request):
    if not request.user.is_admin:
        return redirect('home')
    
    students = User.objects.filter(is_student=True)
    teachers = User.objects.filter(is_teacher=True)
    courses = Course.objects.all()
    
    return render(request, 'courses/admin_dashboard.html', {
        'students': students,
        'teachers': teachers,
        'courses': courses
    })

@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher:
        return redirect('home')
    
    # Показываем все активные курсы преподавателя
    courses = Course.objects.filter(creator=request.user, is_active=True)
    return render(request, 'courses/teacher_dashboard.html', {
        'courses': courses,
        'can_create': True  # Всегда разрешаем создание новых курсов
    })

@login_required
@teacher_required 
def create_course(request):
    if not request.user.is_teacher:
        return redirect('home')
    
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.creator = request.user
            course.save()
            messages.success(request, 'Курс успешно создан!')
            return redirect('teacher_dashboard')
    else:
        form = CourseForm()
    
    return render(request, 'courses/course_form.html', {
        'form': form,
        'title': 'Создание нового курса'
    })

@login_required
@teacher_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, creator=request.user)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Курс успешно обновлен!')
            return redirect('teacher_dashboard')
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'courses/course_form.html', {
        'form': form,
        'title': 'Редактирование курса'
    })

@login_required
@teacher_required
def manage_lessons(request, course_id):
    course = get_object_or_404(Course, id=course_id, creator=request.user)
    
    if request.method == 'POST':
        # Обработка создания урока
        lesson_form = LessonForm(request.POST)
        if lesson_form.is_valid():
            lesson = lesson_form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, 'Урок успешно добавлен!')
            return redirect('manage_lessons', course_id=course.id)
        
        # Обработка создания нового курса из этого же интерфейса
        if 'create_new_course' in request.POST:
            return redirect('create_course')
    else:
        lesson_form = LessonForm()
    
    lessons = course.lessons.all().order_by('order')
    return render(request, 'courses/manage_lessons.html', {
        'course': course,
        'lessons': lessons,
        'lesson_form': lesson_form,
        'can_add_lessons': True  # Всегда разрешаем добавление уроков
    })

@login_required
def take_test(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    questions = lesson.questions.all().order_by('order')
    
    if request.method == 'POST':
        form = TestForm(request.POST, questions=questions)
        if form.is_valid():
            score = calculate_score(form.cleaned_data, questions)
            
            TestResult.objects.create(
                student=request.user,
                lesson=lesson,
                score=score
            )
            
            messages.success(request, f'Тест завершен! Ваш результат: {score}%')
            return redirect('lesson_detail', lesson_id=lesson.id)
    else:
        form = TestForm(questions=questions)
    
    return render(request, 'courses/test_form.html', {
        'lesson': lesson,
        'form': form
    })

def calculate_score(answers, questions):
    total = 0
    correct = 0
    
    for question in questions:
        answer_key = f'question_{question.id}'
        if answer_key in answers:
            if question.question_type == 'text':
                # Простая проверка текстового ответа
                correct += 0.5  # Частичный балл за текстовый ответ
            else:
                selected = set(map(int, answers[answer_key])) if isinstance(answers[answer_key], list) else {int(answers[answer_key])}
                correct_answers = set(a.id for a in question.answers.filter(is_correct=True))
                
                if question.question_type == 'single' and selected == correct_answers:
                    correct += 1
                elif question.question_type == 'multiple' and selected == correct_answers:
                    correct += 1
    
    return int((correct / len(questions)) * 100 if questions else 0)