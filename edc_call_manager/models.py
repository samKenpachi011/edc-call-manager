from django.db import models

from edc_base.model_mixins import BaseUuidModel

from .model_mixins import CallModelMixin, LogModelMixin, LogEntryModelMixin


class Call(CallModelMixin, BaseUuidModel):

    class Meta(CallModelMixin.Meta):
        app_label = 'edc_call_manager'


class Log(LogModelMixin, BaseUuidModel):

    call = models.ForeignKey(Call, on_delete=models.PROTECT)


    class Meta(LogModelMixin.Meta):
        app_label = 'edc_call_manager'


class LogEntry(LogEntryModelMixin, BaseUuidModel):

    log = models.ForeignKey(Log, on_delete=models.PROTECT)

    class Meta(LogEntryModelMixin.Meta):
        app_label = 'edc_call_manager'
