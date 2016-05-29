from datetime import date
from dateutil.relativedelta import relativedelta

from django.core.exceptions import MultipleObjectsReturned, ImproperlyConfigured, ValidationError
from django.utils import timezone
from django.utils.text import slugify

from edc_constants.constants import CLOSED, OPEN, YES


DAILY = 'd'
WEEKLY = 'w'
MONTHLY = 'm'
YEARLY = 'y'


class ModelCaller:
    """A class that manages scheduling and unscheduling of calls to subjects based on the
    creation of given models.

    This class gets registered to site_model_callers and the activity of it's Scheduling and Unscheduling
    models is inspected in signals.
    """

    consent_model = None
    consent_model_subject_foreignkey = None
    locator_model = None
    locator_filter = 'subject_identifier'
    call_model = None  # e.g. Call
    call_model_subject_foreignkey = 'registered_subject'
    log_model = None  # e.g. Log
    log_entry_model = None  # e.g. LogEntry
    interval = None
    label = None
    repeat_times = 0
    unscheduling_model = None

    def __init__(self, model, call_model=None, log_model=None, log_entry_model=None):
        self.model = model
        call_model = call_model or self.call_model
        try:
            self.call_model, self.call_model_subject_foreignkey = self.call_model
        except IndexError:
            self.call_model = call_model or self.call_model
        try:
            self.consent_model, self.consent_model_subject_foreignkey = self.consent_model
        except TypeError:
            pass
        try:
            self.locator_model, self.locator_filter = self.locator_model
        except TypeError:
            pass
        if self.call_model_subject_foreignkey:
            if not [fld.name for fld in self.call_model._meta.fields if fld.name in [self.call_model_subject_foreignkey]]:
                raise ImproperlyConfigured(
                    'ModelCaller model \'{}.{}\' does not have field \'{}\'. See {} declaration for attribute call_model_subject_foreignkey.'.format(
                        self.call_model._meta.app_label, self.call_model._meta.model_name,
                        self.call_model_subject_foreignkey, self.__class__.__name__))
        if self.consent_model and self.consent_model_subject_foreignkey:
            if not [fld.name for fld in self.consent_model._meta.fields if fld.name in [self.consent_model_subject_foreignkey]]:
                raise ImproperlyConfigured(
                    'ModelCaller model \'{}.{}\' does not have field \'{}\'. See {} declaration for attribute consent_model_subject_foreignkey.'.format(
                        self.consent_model._meta.app_label, self.consent_model._meta.model_name,
                        self.consent_model_subject_foreignkey,
                        self.__class__.__name__))
        self.log_model = log_model or self.log_model
        self.log_entry_model = log_entry_model or self.log_entry_model
        for attr in ['locator_model', 'call_model', 'log_model', 'log_entry_model']:
            value = getattr(self, attr)
            if not value:
                raise ImproperlyConfigured(
                    'Attribute {0}.{1} cannot be None. See {0} declaration.'.format(
                        self.__class__.__name__, attr))
        label = self.label or self.__class__.__name__
        self.label = slugify(str(label))
        self.repeats = True if self.unscheduling_model or self.repeat_times > 0 else False
        if self.repeats and self.repeat_times > 0 and self.interval not in [DAILY, WEEKLY, MONTHLY, YEARLY]:
            raise ValueError('ModelCaller expected an \'interval\' for a call scheduled to repeat. Got None.')

    def personal_details(self, instance):
        """Returns additional options to be used to create a Call instance.

        Used if the consent is not available."""
        subject_foreignkey = None
        options = {'subject_identifier': instance.subject_identifier,
                   'first_name': self.get_value(instance, 'first_name'),
                   'initials': self.get_value(instance, 'initials')}
        if ''.join(self.call_model_subject_foreignkey.split('_')) == instance._meta.model_name:
            subject_foreignkey = instance
        else:
            try:
                subject_foreignkey = getattr(instance, self.call_model_subject_foreignkey)
            except AttributeError:
                pass
        if subject_foreignkey:
            options.update({self.call_model_subject_foreignkey: subject_foreignkey})
        return options

    def personal_details_from_consent(self, instance):
        """Returns additional options to be used to create a Call instance.

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
        options = {'subject_identifier': consent.subject_identifier,
                   'first_name': consent.first_name,
                   'initials': consent.initials}
        try:
            consent_foreignkey = getattr(consent, self.consent_model_subject_foreignkey)
            options.update({self.consent_model_subject_foreignkey: consent_foreignkey})
        except AttributeError:
            pass
        return options

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
        log_entries = self.log_entry_model.objects.filter(log=log_entry.log).order_by('-call_datetime')
        if log_entry.pk == log_entries[0].pk:
            call = self.call_model.objects.get(pk=call.pk)
            if call.call_status == CLOSED:
                raise ValidationError('Call is closed. Perhaps catch this in the form.')
            call.call_outcome = '. '.join(log_entry.outcome)
            call.call_datetime = log_entry.call_datetime
            call.call_attempts = log_entries.count()
            if log_entry.may_call == YES:
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
