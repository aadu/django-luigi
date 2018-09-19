import os
import sys

import django
from django.db import models, transaction
from django.apps import apps
from django.conf import settings
import datetime
import logging
from contextlib import contextmanager
from luigi import six
from luigi import configuration
from luigi import task_history
from luigi.task_status import DONE, FAILED, PENDING, RUNNING

from .models import TaskRecord, TaskEvent, TaskParameter
logger = logging.getLogger('django-luigi')


class DjangoTaskHistory(task_history.TaskHistory):
    """
    Task History that writes to a database using django's ORM.
    Also has methods for useful db queries.
    """
    CURRENT_SOURCE_VERSION = 1

    def __init__(self):
        config = configuration.get_config()
        self.tasks = {}  # task_id -> TaskRecord

    def task_scheduled(self, task):
        htask = self._get_task(task, status=PENDING)
        event = TaskEvent(
            event_name=PENDING,
            ts=datetime.datetime.now(),
        )
        self._add_task_event(htask, event)

    def task_finished(self, task, successful):
        event_name = DONE if successful else FAILED
        htask = self._get_task(task, status=event_name)
        event = TaskEvent(
            event_name=event_name,
            ts=datetime.datetime.now(),
        )
        self._add_task_event(htask, event)

    def task_started(self, task, worker_host):
        htask = self._get_task(task, status=RUNNING, host=worker_host)
        event = TaskEvent(
            event_name=RUNNING,
            ts=datetime.datetime.now(),
        )
        self._add_task_event(htask, event)

    def _get_task(self, task, status, host=None):
        if task.id in self.tasks:
            htask = self.tasks[task.id]
            htask.status = status
            if host:
                htask.host = host
        else:
            htask = self.tasks[task.id] = task_history.StoredTask(
                task, status, host)
        return htask

    def _add_task_event(self, task, event):
        for task_record in self._find_or_create_task(task):
            event.task = task_record
            event.save()


    @transaction.atomic()
    def _find_or_create_task(self, task):
        if task.record_id is not None:
            logger.debug(
                "Finding task with record_id [%d]", task.record_id)
            try:
                task_record = TaskRecord.objects.get(pk=task.record_id)
            except TaskRecord.ObjectDoesNotExist:
                raise Exception("Task with record_id, but no matching Task record!")
            if task.host and task.host != task_record.host:
                task_record.host = task.host
                task_record.save()
            yield task_record
        else:
            task_record = TaskRecord.objects.create(
                id=task._task.id, name=task.task_family, host=task.host)
            for k, v in task.parameters.items():
                TaskParameter.objects.create(
                    task=task_record, name=k, value=v
                )
            yield task_record
        task.record_id = task_record.id

    # def find_all_by_parameters(self, task_name, session=None, **task_params):
    #     """
    #     Find tasks with the given task_name and the same parameters as the kwargs.
    #     """
    #     qs = TaskEvent.objects.filter(name=task_name, **task_params).prefetch_related('parameters')
    #     for k, v in task_params.items():
    #         qs = qs.annotate(**{k})

    #     with self._session(session) as session:
    #         query = session.query(TaskRecord).join(
    #             TaskEvent).filter(TaskRecord.name == task_name)
    #         for (k, v) in six.iteritems(task_params):
    #             alias = sqlalchemy.orm.aliased(TaskParameter)
    #             query = query.join(alias).filter(
    #                 alias.name == k, alias.value == v)

    #         tasks = query.order_by(TaskEvent.ts)
    #         for task in tasks:
    #             # Sanity check
    #             assert all(k in task.parameters and v == str(
    #                 task.parameters[k].value) for (k, v) in six.iteritems(task_params))

    #             yield task

    # def find_all_by_name(self, task_name, session=None):
    #     """
    #     Find all tasks with the given task_name.
    #     """
    #     return self.find_all_by_parameters(task_name, session)

    # def find_latest_runs(self, session=None):
    #     """
    #     Return tasks that have been updated in the past 24 hours.
    #     """
    #     with self._session(session) as session:
    #         yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    #         return session.query(TaskRecord).\
    #             join(TaskEvent).\
    #             filter(TaskEvent.ts >= yesterday).\
    #             group_by(TaskRecord.id, TaskEvent.event_name, TaskEvent.ts).\
    #             order_by(TaskEvent.ts.desc()).\
    #             all()

    # def find_all_runs(self, session=None):
    #     """
    #     Return all tasks that have been updated.
    #     """
    #     with self._session(session) as session:
    #         return session.query(TaskRecord).all()

    # def find_all_events(self, session=None):
    #     """
    #     Return all running/failed/done events.
    #     """
    #     with self._session(session) as session:
    #         return session.query(TaskEvent).all()

    # def find_task_by_id(self, id, session=None):
    #     """
    #     Find task with the given record ID.
    #     """
    #     with self._session(session) as session:
    #         return session.query(TaskRecord).get(id)
