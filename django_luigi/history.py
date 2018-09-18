from django.db import models


class TableUpdates(models.Model):
    update_id = models.CharField(max_length=128, null=False, primary_key=True)
    target_model = models.CharField(max_length=128)
    inserted = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'table_updates'

import datetime
import logging
from contextlib import contextmanager
from django.apps import apps
from django.conf import settings
from luigi import six

from luigi import configuration
from luigi import task_history
from luigi.task_status import DONE, FAILED, PENDING, RUNNING

import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import sqlalchemy.orm.collections
from sqlalchemy.engine import reflection

logger = logging.getLogger('django-luigi')

from . import models


class DjangoTaskHistory(task_history.TaskHistory):
    """
    Task History that writes to a database using django's ORM.
    Also has methods for useful db queries.
    """
    CURRENT_SOURCE_VERSION = 1

    def setup_django(self):
        if not apps.ready and not settings.configured:
            sys.path.append(self.django_root)
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", self.settings_path)
            django.setup()

        self.marker_model_bound = apps.get_model(
            'django_luigi', self.marker_model)

        if self.marker_model is None:
            self.marker_model = luigi.configuration.get_config().get(
                'django', 'marker-model', 'TableUpdates')
        if not apps.ready and not settings.configured:

    def __init__(self):
        config = configuration.get_config()
        connection_string = config.get('task_history', 'db_connection')
        self.engine = sqlalchemy.create_engine(connection_string)
        self.session_factory = sqlalchemy.orm.sessionmaker(
            bind=self.engine, expire_on_commit=False)
        Base.metadata.create_all(self.engine)
        self.tasks = {}  # task_id -> TaskRecord

        _upgrade_schema(self.engine)

    def task_scheduled(self, task):
        htask = self._get_task(task, status=PENDING)
        event = models.TaskEvent(
            event_name=PENDING,
            ts=datetime.datetime.now(),
        )
        self._add_task_event(htask, event)

    def task_finished(self, task, successful):
        event_name = DONE if successful else FAILED
        htask = self._get_task(task, status=event_name)
        event = models.TaskEvent(
            event_name=event_name,
            ts=datetime.datetime.now(),
        )
        self._add_task_event(htask, event)

    def task_started(self, task, worker_host):
        htask = self._get_task(task, status=RUNNING, host=worker_host)
        event = models.TaskEvent(
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

    def _find_or_create_task(self, task):
        if task.record_id is not None:
            logger.debug(
                "Finding task with record_id [%d]", task.record_id)
            task_record = models.TaskRecord.objects.get(pk=task.record_id)
            if not task_record:
                raise Exception(
                    "Task with record_id, but no matching Task record!")
            yield task_record
        else:
            task_record = models.TaskRecord(
                id=task._task.id, name=task.task_family, host=task.host)
            for (k, v) in six.iteritems(task.parameters):
                task_record.parameters[k] = TaskParameter(name=k, value=v)
            session.add(task_record)
            yield (task_record, session)
        if task.host:
            task_record.host = task.host
        task.record_id = task_record.id

    def find_all_by_parameters(self, task_name, session=None, **task_params):
        """
        Find tasks with the given task_name and the same parameters as the kwargs.
        """
        with self._session(session) as session:
            query = session.query(TaskRecord).join(
                TaskEvent).filter(TaskRecord.name == task_name)
            for (k, v) in six.iteritems(task_params):
                alias = sqlalchemy.orm.aliased(TaskParameter)
                query = query.join(alias).filter(
                    alias.name == k, alias.value == v)

            tasks = query.order_by(TaskEvent.ts)
            for task in tasks:
                # Sanity check
                assert all(k in task.parameters and v == str(
                    task.parameters[k].value) for (k, v) in six.iteritems(task_params))

                yield task

    def find_all_by_name(self, task_name, session=None):
        """
        Find all tasks with the given task_name.
        """
        return self.find_all_by_parameters(task_name, session)

    def find_latest_runs(self, session=None):
        """
        Return tasks that have been updated in the past 24 hours.
        """
        with self._session(session) as session:
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            return session.query(TaskRecord).\
                join(TaskEvent).\
                filter(TaskEvent.ts >= yesterday).\
                group_by(TaskRecord.id, TaskEvent.event_name, TaskEvent.ts).\
                order_by(TaskEvent.ts.desc()).\
                all()

    def find_all_runs(self, session=None):
        """
        Return all tasks that have been updated.
        """
        with self._session(session) as session:
            return session.query(TaskRecord).all()

    def find_all_events(self, session=None):
        """
        Return all running/failed/done events.
        """
        with self._session(session) as session:
            return session.query(TaskEvent).all()

    def find_task_by_id(self, id, session=None):
        """
        Find task with the given record ID.
        """
        with self._session(session) as session:
            return session.query(TaskRecord).get(id)
