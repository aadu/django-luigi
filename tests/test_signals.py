import pytest
from django.utils import timezone
from tests.tasks import MoreComplexTask, build
from django_luigi.models import TaskRecord


import pytest

@pytest.mark.django_db
def test_my_user():
    assert not TaskRecord.objects.filter(name='MoreComplexTask', parameters__value='bob').exists()
    build([MoreComplexTask(name='bob', job=33, time=timezone.now())])
    assert TaskRecord.objects.filter(name='MoreComplexTask', parameters__value='bob').exists()
