from django.contrib.auth.models import AbstractUser
from django.db import models
from enum import Enum
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOISES = (
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(
        'Email адрес',
        unique=True,
        help_text='Обязательное поле. Не более 254 символов.'
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        'Роль',
        max_length=20,
        choices=ROLE_CHOISES,
        default='user',
    )
    confirmation_code = models.TextField(
        'Код подтверждения',
        blank=True,
    )

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_moderator(self):
        return self.role == 'moderator'


class Project(models.Model):
    name = models.CharField('Название проекта', max_length=255)
    description = models.TextField('Описание', blank=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='projects', verbose_name='Автор'
    )
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', auto_now=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.name


class Task(models.Model):
    class StatusEnum(Enum):
        TODO = 'todo'
        IN_PROGRESS = 'in_progress'
        DONE = 'done'

        @classmethod
        def choices(cls):
            return [
                (cls.TODO.value, _('To do')),
                (cls.IN_PROGRESS.value, _('In progress')),
                (cls.DONE.value, _('Done')),
            ]

    class Priority(Enum):
        LOW = 1
        MEDIUM = 2
        HIGH = 3

        @classmethod
        def choices(cls):
            return [
                (cls.LOW.value, _('Low')),
                (cls.MEDIUM.value, _('Medium')),
                (cls.HIGH.value, _('High')),
            ]

    status = models.CharField(
        'Статус',
        max_length=20,
        choices=StatusEnum.choices(),
        default=StatusEnum.TODO.value,
    )

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='tasks', verbose_name='Проект'
    )
    title = models.CharField('Заголовок', max_length=255)
    description = models.TextField('Описание', blank=True)
    priority = models.IntegerField(
        'Приоритет', choices=Priority.choices(), default=Priority.MEDIUM.value
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tasks_authored', verbose_name='Автор'
    )
    assignee = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tasks_assigned', verbose_name='Исполнитель'
    )
    due_date = models.DateField('Срок', null=True, blank=True)
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return f'{self.title} ({self.get_status_display()})'
