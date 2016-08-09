from django.db import models
from django.utils import timezone

from edc_base.model.models.base_uuid_model import BaseUuidModel
from edc_locator.models import LocatorMixin
from edc_registration.models import RegisteredSubjectModelMixin

from edc_base.model.models.historical_records import HistoricalRecords
from edc_call_manager.model_mixins import CallModelMixin, LogModelMixin, LogEntryModelMixin


class RegisteredSubject(RegisteredSubjectModelMixin, BaseUuidModel):

    class Meta:
        app_label = 'edc_call_manager_example'


class TestModel(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)

    report_datetime = models.DateField(
        default=timezone.now)

    class Meta:
        app_label = 'edc_call_manager_example'


class Locator(LocatorMixin, BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)

    class Meta:
        app_label = 'edc_call_manager_example'


class TestStartModel(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)

    report_datetime = models.DateField(
        default=timezone.now)

    class Meta:
        app_label = 'edc_call_manager_example'


class TestStopModel(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)

    report_datetime = models.DateField(
        default=timezone.now)

    class Meta:
        app_label = 'edc_call_manager_example'


class Call(CallModelMixin, BaseUuidModel):

    history = HistoricalRecords()

    class Meta(CallModelMixin.Meta):
        app_label = 'edc_call_manager_example'


class Log(LogModelMixin, BaseUuidModel):

    call = models.ForeignKey(Call)

    history = HistoricalRecords()

    class Meta(LogModelMixin.Meta):
        app_label = 'edc_call_manager_example'


class LogEntry(LogEntryModelMixin, BaseUuidModel):

    log = models.ForeignKey(Log)

    history = HistoricalRecords()

    class Meta(LogEntryModelMixin.Meta):
        app_label = 'edc_call_manager_example'
