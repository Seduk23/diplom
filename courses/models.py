from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

class CustomUser(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_superuser:  # Админы автоматически получают все права
            self.is_admin = True
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
User = get_user_model()

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

    def __str__(self):
        return self.title
    
class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="Курс",
        related_name='lessons'
    )
    title = models.CharField("Название", max_length=200)
    content = models.TextField("Содержание")
    order = models.PositiveIntegerField("Порядок", default=0)
    is_published = models.BooleanField("Опубликован", default=False)

    class Meta:
        ordering = ['order']
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
class Question(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField("Текст вопроса")
    question_type = models.CharField("Тип вопроса", max_length=20, choices=[
        ('single', 'Один вариант'),
        ('multiple', 'Несколько вариантов'),
        ('text', 'Текстовый ответ')
    ])
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        ordering = ['order']

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField("Текст ответа")
    is_correct = models.BooleanField("Правильный ответ", default=False)

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