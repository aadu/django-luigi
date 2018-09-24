from django.contrib import admin
from django_luigi.models import TaskRecord, TaskEvent, TaskParameter


class ReadOnlyAdminMixin:
    min_num = 0
    can_delete = False

    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class InlineTaskEventAdmin(ReadOnlyAdminMixin, admin.TabularInline):
    show_change_link = True
    model = TaskEvent


class InlineTaskParameterAdmin(ReadOnlyAdminMixin, admin.TabularInline):
    model = TaskParameter


@admin.register(TaskRecord)
class TaskRecordAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    # readonly_fields = ('name', 'namespace', 'host')
    list_filter = ('name', 'namespace')
    list_display = ('task_id', 'name', 'namespace', 'host',)
    inlines = [
        InlineTaskParameterAdmin,
        InlineTaskEventAdmin,
    ]


@admin.register(TaskEvent)
class TaskEventAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ('task', 'name', 'timestamp', 'message')
    list_filter = ('name', 'timestamp')
    ordering = ['timestamp']


