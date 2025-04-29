import os
import django

# Указываем Django, какие настройки использовать
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'js_learning.settings')
django.setup()

from courses.models import Course
from django.contrib.auth import get_user_model

User = get_user_model()

def set_defaults():
    # Находим или создаем администратора
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
    
    # Устанавливаем создателя и дату для всех курсов
    for course in Course.objects.all():
        if not course.creator:
            course.creator = admin
            course.save()

if __name__ == '__main__':
    set_defaults()
    print("Данные успешно обновлены!")