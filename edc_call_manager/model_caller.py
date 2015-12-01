from edc_call_manager.models import Call, Log
from django.utils.text import slugify
from edc_constants.constants import CLOSED

DAILY = 'd'
WEEKLY = 'w'
MONTHLY = 'm'
YEARLY = 'y'


class ModelCaller:

    label = None
    unscheduling_model = None
    interval = None
    repeat_times = 0

    def __init__(self, model):
        self.model = model
        label = self.label or self.__class__.__name__
        self.label = slugify(label)
        self.repeats = True if self.unscheduling_model or self.repeat_times > 0 else False
        if self.repeats and self.interval not in [DAILY, WEEKLY, MONTHLY, YEARLY]:
            raise ValueError('ModelCaller expected an \'interval\' for a call scheduled to repeat. Got None.')

    def schedule_call(self, instance):
        call = Call.objects.create(
            subject_identifier=instance.subject_identifier,
            label=self.label,
            repeats=self.repeats)
        Log.objects.create(
            call=call)

    def unschedule_call(self, instance):
        try:
            call = Call.objects.get(
                subject_identifier=instance.subject_identifier,
                label=self.label)
            call.call_status = CLOSED
            call.save()
        except Call.DoesNotExist:
            pass
