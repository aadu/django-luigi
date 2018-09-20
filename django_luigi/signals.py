import logging

import django.dispatch
import luigi

logger = logging.getLogger(__name__)

dependency_discovered = django.dispatch.Signal(providing_args=["task", "dependency"])
dependency_missing = django.dispatch.Signal(providing_args=["task"])
dependency_present = django.dispatch.Signal(providing_args=["task"])
broken_task = django.dispatch.Signal(providing_args=["task", "exception"])
start = django.dispatch.Signal(providing_args=["task"])
progress = django.dispatch.Signal(providing_args=["task", "info"])
failure = django.dispatch.Signal(providing_args=["task", "exception"])
success = django.dispatch.Signal(providing_args=["task"])
processing_time = django.dispatch.Signal(providing_args=["task", "duration"])
timeout = django.dispatch.Signal(providing_args=["task", "error_msg"])
process_failure = django.dispatch.Signal(providing_args=["task", "error_msg"])


@luigi.Task.event_handler(luigi.Event.DEPENDENCY_DISCOVERED)
def _send_dependency_discovered_signal(task, dep):
    dependency_discovered.send(luigi.Task, task=task, dependency=dep)


@luigi.Task.event_handler(luigi.Event.DEPENDENCY_MISSING)
def _send_dependency_missing_signal(task):
    dependency_missing.send(luigi.Task, task=task)


@luigi.Task.event_handler(luigi.Event.DEPENDENCY_PRESENT)
def _send_dependency_present_signal(task):
    dependency_present.send(luigi.Task, task=task)


@luigi.Task.event_handler(luigi.Event.BROKEN_TASK)
def _send_broken_task_signal(task, ex):
    broken_task.send(luigi.Task, task=task, exception=ex)


@luigi.Task.event_handler(luigi.Event.START)
def _send_start_signal(task):
    start.send(luigi.Task, task=task)


@luigi.Task.event_handler(luigi.Event.SUCCESS)
def _send_success_signal(task):
    success.send(luigi.Task, task=task)


@luigi.Task.event_handler(luigi.Event.PROCESSING_TIME)
def _send_processing_time_signal(task, dur):
    processing_time.send(luigi.Task, task=task, duration=dur)


@luigi.Task.event_handler(luigi.Event.TIMEOUT)
def _send_timeout_signal(task, error_msg):
    timeout.send(luigi.Task, task=task, error_msg=error_msg)


@luigi.Task.event_handler(luigi.Event.PROCESS_FAILURE)
def _send_process_failure_signal(task, error_msg):
    process_failure.send(luigi.Task, task=task, error_msg=error_msg)
