from django.contrib import admin
from django_luigi.models import TaskRecord, TaskEvent, TaskParameter

admin.site.register(TaskRecord)
admin.site.register(TaskEvent)
admin.site.register(TaskParameter)
