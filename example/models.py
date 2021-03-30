from django.db import models
from django.utils import timezone
from edc_base.model_mixins import BaseUuidModel
from edc_call_manager.model_mixins import CallModelMixin, LogModelMixin, LogEntryModelMixin
from edc_locator.model_mixins import LocatorModelMixin


class TestModel(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)

    report_datetime = models.DateField(
        default=timezone.now)

    objects = models.Manager()

    class Meta:
        app_label = 'example'


class Locator(LocatorModelMixin, BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)

    class Meta:
        app_label = 'example'


class TestStartModel(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)

    report_datetime = models.DateField(
        default=timezone.now)

    objects = models.Manager()

    class Meta:
        app_label = 'example'


class TestStopModel(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)

    report_datetime = models.DateField(
        default=timezone.now)

    objects = models.Manager()

    class Meta:
        app_label = 'example'

class TestStopTwoModel(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)

    report_datetime = models.DateField(
        default=timezone.now)

    objects = models.Manager()

    class Meta:
        app_label = 'example'


class Call(CallModelMixin, BaseUuidModel):

    objects = models.Manager()

    class Meta(CallModelMixin.Meta):
        app_label = 'example'


class Log(LogModelMixin, BaseUuidModel):

    call = models.ForeignKey(Call, on_delete=models.CASCADE)

    objects = models.Manager()

    class Meta(LogModelMixin.Meta):
        app_label = 'example'


class LogEntry(LogEntryModelMixin, BaseUuidModel):

    log = models.ForeignKey(Log, on_delete=models.CASCADE)

    objects = models.Manager()

    class Meta(LogEntryModelMixin.Meta):
        app_label = 'example'
