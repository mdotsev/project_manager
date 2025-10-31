from django.contrib import admin

from .models import Project, Task, User


class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'project', 'status', 'priority', 'assignee', 'author', 'created_at'
    )
    list_editable = ('status', 'priority', 'assignee')
    search_fields = ('title', 'description')
    list_filter = ('status', 'priority', 'project')
    empty_value_display = '-пусто-'


admin.site.register(User)
admin.site.register(Project)
admin.site.register(Task, TaskAdmin)
