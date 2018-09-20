from django.db import models, transaction
from django.dispatch import receiver
from django.utils import timezone
from . import signals

class Status:
    START = 'START'
    FAILURE = 'FAILURE'
    SUCCESS = 'SUCCESS'


class TableUpdates(models.Model):
    update_id = models.CharField(max_length=128, unique=True)
    target_model = models.CharField(max_length=128)
    inserted = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'table_updates'

class TaskRecord(models.Model):
    """
    Base table to track information about a luigi.Task.
    References to other tables are available through task.events, task.parameters, etc.
    """
    task_id = models.CharField(
        max_length=200, db_index=True, unique=True, editable=False)
    name = models.CharField(max_length=128, db_index=True, editable=False)
    namespace = models.CharField(max_length=128, null=True, editable=False)
    host = models.CharField(max_length=128, null=True, editable=False)

    class Meta:
        db_table = 'tasks'
        default_related_name = 'tasks'

    def __str__(self):
        return "TaskRecord(name=%s, host=%s)" % (self.name, self.host)


class TaskParameter(models.Model):
    """
    Table to track luigi.Parameter()s of a Task.
    """
    task = models.ForeignKey('TaskRecord', on_delete=models.CASCADE, editable=False)
    name = models.CharField(max_length=128, db_index=True, editable=False)
    value = models.TextField(null=True, editable=False)

    def __str__(self):
        return "TaskParameter(task_id=%d, name=%s, value=%s)" % (self.task_id, self.name, self.value)

    class Meta:
        db_table = 'task_parameters'
        unique_together = (('task', 'name'),)
        default_related_name = 'parameters'


class TaskEvent(models.Model):
    """
    Table to track when a task is scheduled, starts, finishes, and fails.
    """
    task = models.ForeignKey('TaskRecord', on_delete=models.CASCADE, editable=False)
    name = models.CharField(max_length=24, editable=False)
    ts = models.DateTimeField(db_index=True, editable=False, auto_now_add=True)

    def __str__(self):
        return "TaskEvent(task_id=%s, name=%s, ts=%s" % (self.task_id, self.name, self.ts)

    class Meta:
        db_table = 'task_events'
        default_related_name = 'events'



@transaction.atomic()
def register_task_event(task, event, **kwargs):
    defaults = {
        'name': task.get_task_family(),
        'namespace': task.get_task_namespace(),
    }
    task_record, _ = TaskRecord.objects.update_or_create(
        task_id=task.task_id,
        defaults=defaults,
    )
    for key, value in task.param_kwargs.items():
        TaskParameter.objects.get_or_create(
            task=task_record,
            name=key,
            value=value,
        )
    TaskEvent.objects.create(
        task=task_record,
        name=event,
        ts=timezone.now(),
    )


@receiver(signals.start)
def register_task_start(sender, task, **kwargs):
    register_task_event(task, Status.START)


@receiver(signals.failure)
def register_task_failure(sender, task, **kwargs):
    register_task_event(task, Status.FAILURE)


@receiver(signals.success)
def register_task_success(sender, task, **kwargs):
    register_task_event(task, Status.SUCCESS)
