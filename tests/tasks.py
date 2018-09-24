from luigi import build, Task, LocalTarget
import luigi
import django
from django.utils import timezone

django.setup()

from django_luigi import models, signals


class DummyTask(Task):
    task_namespace = 'bob'

    def output(self):
        return LocalTarget('example.txt')

    def run(self):
        print("HEY")



class MoreComplexTask(Task):
    name = luigi.Parameter()
    job = luigi.IntParameter()
    time = luigi.DateParameter()

    def output(self):
        return LocalTarget("Not-a-burger.txt")

    def run(self):
        import time
        time.sleep(10)


if __name__ == '__main__':
    build([DummyTask()])
    build([MoreComplexTask(name='bob', job=33, time=timezone.now())])
