from django.db import models
from django.utils import timezone

from edc_call_manager.models import CallModelMixin, LogModelMixin, LogEntryModelMixin
from edc_locator.models import LocatorMixin
from edc_registration.models import RegisteredSubjectModelMixin
from edc_base.model.models.base_uuid_model import BaseUuidModel


class RegisteredSubject(RegisteredSubjectModelMixin, BaseUuidModel):

    class Meta:
        app_label = 'example'


class Call(CallModelMixin, BaseUuidModel):

    registered_subject = models.ForeignKey(RegisteredSubject)

    class Meta:
        app_label = 'example'


class Log(LogModelMixin, BaseUuidModel):

    call = models.ForeignKey(Call)

    class Meta:
        app_label = 'example'


class LogEntry(LogEntryModelMixin, BaseUuidModel):

    log = models.ForeignKey(Log)

    class Meta:
        app_label = 'example'


class TestModel(BaseUuidModel):

    registered_subject = models.ForeignKey(RegisteredSubject)

    subject_identifier = models.CharField(
        max_length=25)

    report_datetime = models.DateField(
        default=timezone.now)

    class Meta:
        app_label = 'example'


class Locator(LocatorMixin, BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)

    class Meta:
        app_label = 'example'


class TestStartModel(BaseUuidModel):

    registered_subject = models.ForeignKey(RegisteredSubject)

    subject_identifier = models.CharField(
        max_length=25)

    report_datetime = models.DateField(
        default=timezone.now)

    class Meta:
        app_label = 'example'


class TestStopModel(BaseUuidModel):

    registered_subject = models.ForeignKey(RegisteredSubject)

    subject_identifier = models.CharField(
        max_length=25)

    report_datetime = models.DateField(
        default=timezone.now)

    class Meta:
        app_label = 'example'
