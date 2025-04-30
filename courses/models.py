from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
 
class Course(models.Model):
    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание")
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Создатель",
        related_name='courses'
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def can_view(self, user):
        if user.is_admin or user.is_teacher:
            return True
        return self.is_active and (user.is_student and self in user.courses_enrolled.all())
    
    def __str__(self):
        return self.title

# models.py
class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)  # Основной текст урока
    video_url = models.URLField(blank=True)  # Ссылка на видео
    image = models.ImageField(upload_to='lesson_images/', blank=True)  # Изображение для урока
    order = models.PositiveIntegerField(default=0)  # Порядок урока в курсе
    created_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=False, verbose_name="Опубликован")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
    
class Test(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='test')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    passing_score = models.PositiveIntegerField(default=70)  # Проходной балл в %
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Тест к уроку: {self.lesson.title}"    
    
# models.py
class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(
        max_length=20,
        choices=(
            ('single', 'Один правильный ответ'),
            ('multiple', 'Несколько правильных ответов'),
            ('text', 'Текстовый ответ'),
        ),
        default='single'
    )
    order = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=1)  # Баллы за вопрос

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.text[:50]}..."

# models.py
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.text[:50]}... ({'верный' if self.is_correct else 'неверный'})"

class TestResult(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='test_results'
    )
    lesson = models.ForeignKey(
        'Lesson',
        on_delete=models.CASCADE,
        related_name='test_results'
    )
    score = models.FloatField()
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'lesson']
        verbose_name = 'Результат теста'
        verbose_name_plural = 'Результаты тестов'

    def __str__(self):
        return f"{self.student.username} - {self.lesson.title} ({self.score}%)"
    