from django.db import models

from edc_base.model_mixins import BaseUuidModel
from edc_base.model_managers import HistoricalRecords

from .model_mixins import CallModelMixin, LogModelMixin, LogEntryModelMixin


class Call(CallModelMixin, BaseUuidModel):

    history = HistoricalRecords()

    class Meta(CallModelMixin.Meta):
        app_label = 'edc_call_manager'


class Log(LogModelMixin, BaseUuidModel):

    call = models.ForeignKey(Call)

    history = HistoricalRecords()

    class Meta(LogModelMixin.Meta):
        app_label = 'edc_call_manager'


class LogEntry(LogEntryModelMixin, BaseUuidModel):

    log = models.ForeignKey(Log)

    history = HistoricalRecords()

    class Meta(LogEntryModelMixin.Meta):
        app_label = 'edc_call_manager'
