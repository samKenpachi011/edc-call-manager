from collections import namedtuple
from datetime import date
from django.core.exceptions import MultipleObjectsReturned
from django.utils import timezone
from django.utils.text import slugify

from edc_call_manager.models import Call, Log, LogEntry
from edc_constants.constants import CLOSED, OPEN, YES
from dateutil.relativedelta import relativedelta


DAILY = 'd'
WEEKLY = 'w'
MONTHLY = 'm'
YEARLY = 'y'

Subject = namedtuple('Person', 'registered_subject subject_identifier first_name initials')


class ModelCaller:
    """A class that manages scheduling and unscheduling of calls to subjects based on the
    creation of given models.

    This class gets registered to site_model_callers and the activity of it's Scheduling and Unscheduling
    models is inspected in signals.
    """

    consent_model = None
    locator_model = None
    locator_filter = 'subject_identifier'
    call_model = Call
    log_model = Log
    interval = None
    label = None
    repeat_times = 0
    unscheduling_model = None

    def __init__(self, model):
        self.model = model
        label = self.label or self.__class__.__name__
        self.label = slugify(str(label))
        self.repeats = True if self.unscheduling_model or self.repeat_times > 0 else False
        if self.repeats and self.interval not in [DAILY, WEEKLY, MONTHLY, YEARLY]:
            raise ValueError('ModelCaller expected an \'interval\' for a call scheduled to repeat. Got None.')

    def personal_details(self, instance):
        """Returns a namedtuple of subject details.

        Override to supply another source of this information, e.g. RegisteredSubject."""
        try:
            registered_subject = instance.registered_subject
        except AttributeError:
            registered_subject = None
        return Subject(
            registered_subject=registered_subject,
            subject_identifier=instance.subject_identifier,
            first_name=self.get_value(instance, 'first_name'),
            initials=self.get_value(instance, 'initials'))._asdict()

    def personal_details_from_consent(self, instance):
        """Returns a namedtuple with values from the consent model.

        You should use the edc_consent RequiresConsentMixin on the scheduling and unscheduling models to
        avoid hitting the ValueError below when the subject is not consented."""
        try:
            consent = self.consent_model.objects.get(subject_identifier=instance.subject_identifier)
        except MultipleObjectsReturned:
            consent = self.consent_model.consent.valid_consent_for_period(
                instance.subject_identifier, timezone.now())
        except self.consent_model.DoesNotExist as e:
            raise ValueError(
                'ModelCaller \'{}\' is configured to require a consent for subject \'{}\'. '
                'Got \'{}\''.format(self.label, instance.subject_identifier, str(e)))
        return Subject(
            registered_subject=consent.registered_subject,
            subject_identifier=consent.subject_identifier,
            first_name=consent.first_name,
            initials=consent.initials)._asdict()

    def schedule_call(self, instance, scheduled=None):
        """Schedules a call by creating a new call instance and creates the corresponding Log instance."""
        if self.consent_model:
            options = self.personal_details_from_consent(instance)
        else:
            options = self.personal_details(instance)
        call = self.call_model.objects.create(
            scheduled=scheduled or date.today(),
            label=self.label,
            repeats=self.repeats,
            **options)
        self.log_model.objects.create(
            call=call,
            locator_information=self.get_locator(instance))

    def unschedule_call(self, instance):
        """Unschedules any calls for this subject and model caller."""
        self.call_model.objects.filter(subject_identifier=instance.subject_identifier, label=self.label).exclude(
            call_status=CLOSED).update(call_status=CLOSED, auto_closed=True)

    def schedule_next_call(self, call, scheduled_date=None):
        """Schedules the next call if either scheduled_date is provided or can be calculated."""
        scheduled_date = scheduled_date or self.get_next_scheduled_date(call.call_datetime)
        if scheduled_date:
            self.schedule_call(call, scheduled_date)

    def get_next_scheduled_date(self, reference_date):
        """Returns the next scheduled date or None based on the interval.

        TODO: This needs to be a bit more sophisticated to avoid holidays, weekends, etc."""
        scheduled_date = None
        if self.interval == DAILY:
            scheduled_date = reference_date + relativedelta(days=+1)
        elif self.interval == WEEKLY:
            scheduled_date = reference_date + relativedelta(days=+1, weekday=reference_date.weekday())
        elif self.interval == MONTHLY:
            scheduled_date = reference_date + relativedelta(months=+1, weekday=reference_date.weekday())
        else:
            pass
        return scheduled_date

    def update_call_from_log(self, call, log_entry, commit=True):
        """Updates the call_model instance with information from the log entry
        for this subject and model caller.

        Only updates call if this is the most recent log_entry."""
        log_entries = LogEntry.objects.filter(log=log_entry.log).order_by('-call_datetime')
        if log_entry.pk == log_entries[0].pk:
            call = Call.objects.get(pk=call.pk)
            if call.call_status == CLOSED:
                raise ValueError('Call is unexpectedly closed.')
            call.call_outcome = '. '.join(log_entry.outcome)
            call.call_datetime = log_entry.call_datetime
            call.call_attempts = log_entries.count()
            if log_entry.call_again == YES:
                call.call_status = OPEN
            else:
                call.call_status = CLOSED
            call.modified = log_entry.modified
            call.user_modified = log_entry.user_modified
            if commit:
                call.save()

    def get_locator(self, instance):
        """Returns the locator instance as a formatted string."""
        locator = ''
        if self.locator_model:
            locator_filter = self.locator_filter or 'subject_identifier'
            options = {locator_filter: instance.subject_identifier}
            try:
                locator = self.locator_model.objects.get(**options)
                locator = locator.to_string()
            except self.locator_model.DoesNotExist:
                locator = 'locator not found.'
        return locator

    def get_value(self, instance, attr):
        try:
            value = getattr(instance, attr)
        except AttributeError:
            value = None
        return value
