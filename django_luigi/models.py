from django.db import models


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
    task_id = models.CharField(max_length=200, db_index=True)
    name = models.CharField(max_length=128, db_index=True)
    host = models.CharField(max_length=128)

    class Meta:
        db_table = 'tasks'

    def __repr__(self):
        return "TaskRecord(name=%s, host=%s)" % (self.name, self.host)


class TaskParameter(models.Model):
    """
    Table to track luigi.Parameter()s of a Task.
    """
    task = models.ForeignKey(TaskRecord, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, db_index=True)
    value = models.TextField()

    def __repr__(self):
        return "TaskParameter(task_id=%d, name=%s, value=%s)" % (self.task_id, self.name, self.value)

    class Meta:
        db_table = 'task_parameters'
        unique_together = (('task', 'name'),)


class TaskEvent(models.Model):
    """
    Table to track when a task is scheduled, starts, finishes, and fails.
    """
    task = models.ForeignKey(TaskRecord, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=20)
    ts = models.DateTimeField(blank=True, null=True, db_index=True)

    def __repr__(self):
        return "TaskEvent(task_id=%s, event_name=%s, ts=%s" % (self.task_id, self.event_name, self.ts)

    class Meta:
        db_table = 'task_events'
