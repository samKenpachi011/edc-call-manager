from datetime import date
from dateutil.relativedelta import relativedelta

from django.apps import apps as django_apps
from django.core.exceptions import MultipleObjectsReturned, ImproperlyConfigured, ValidationError
from django.utils.text import slugify

from edc_base.utils import get_utcnow
from edc_constants.constants import CLOSED, YES, DEAD, NO

from .constants import DAILY, WEEKLY, MONTHLY, YEARLY, OPEN_CALL, NEW_CALL
from .exceptions import ModelCallerError

app_config = django_apps.get_app_config('edc_call_manager')


class ModelCaller:
    """A class that manages scheduling and unscheduling of calls to subjects based on the
    creation of given models.

    This class gets registered to site_model_callers and the activity of it's Scheduling and Unscheduling
    models is inspected in signals.

    """
    consent_model = None
    interval = None
    label = None
    locator_filter = 'subject_identifier'
    locator_model = None
    repeat_times = 0
    subject_model = None  # model with PII attrs. Default: RegisteredSubject
    verbose_name = None

    def __init__(self, start_model, stop_model):
        self.consent_model_fk = None
        self.start_model = start_model
        self.start_model_name = start_model._meta.label
        self.stop_model = stop_model
        if self.stop_model:
            self.stop_model_name = stop_model._meta.label
        try:
            self.call_model = django_apps.get_model('edc_call_manager.call')
            self.log_model = django_apps.get_model('edc_call_manager.log')
            self.log_entry_model = django_apps.get_model('edc_call_manager.logentry')
        except LookupError as e:
            raise ModelCallerError('{} Try setting \'app_label\' to the app where the model is declared '
                                   'in AppConfig'.format(str(e), self.__class__.__name__))
        if not self.subject_model:
            try:
                self.subject_model = django_apps.get_model(
                    'edc_registration.registeredsubject')
            except LookupError as e:
                raise ModelCallerError(
                    'Cannot determine subject_model. Got {}'.format(str(e)))
        self.subject_model_name = self.subject_model._meta.label
        try:
            self.consent_model, self.consent_model_fk = self.consent_model
        except TypeError:
            pass
        try:
            self.locator_model, self.locator_filter = self.locator_model
        except TypeError:
            pass
        self.locator_model_name = self.locator_model._meta.label
        if self.consent_model and self.consent_model_fk:
            if not [fld.name for fld in self.consent_model._meta.fields if fld.name in [self.consent_model_fk]]:
                raise ImproperlyConfigured(
                    'ModelCaller model \'{}.{}\' does not have field \'{}\'. See {} declaration for '
                    'attribute consent_model_fk.'.format(
                        self.consent_model._meta.app_label, self.consent_model._meta.model_name,
                        self.consent_model_fk,
                        self.__class__.__name__))
        for attr in ['locator_model', 'call_model', 'log_model', 'log_entry_model']:
            value = getattr(self, attr)
            if not value:
                raise ImproperlyConfigured(
                    'Attribute {0}.{1} cannot be None. See {0} declaration.'.format(
                        self.__class__.__name__, attr))
        if self.consent_model:
            self.consent_model_name = self.consent_model._meta.label
        label = self.label or self.__class__.__name__
        self.label = slugify(str(label))
        if self.interval not in [DAILY, WEEKLY, MONTHLY, YEARLY, None]:
            raise ValueError(
                'ModelCaller expected an \'interval\' for a call scheduled to repeat. Got None.')
        self.repeats = False
        if self.stop_model:
            if self.repeat_times > 0 or self.interval:
                self.repeats = True

    def personal_details_from_subject(self, instance):
        """Returns additional options from the subject model to be used to create a Call instance.

        Used if the consent is not available."""
        subject = self.subject(instance.subject_identifier)
        if subject:
            options = {'subject_identifier': subject.subject_identifier,
                       'first_name': subject.first_name,
                       'initials': subject.initials}
        else:
            options = {'subject_identifier': instance.subject_identifier}
        return options

    def personal_details_from_consent(self, instance):
        """Returns additional options from the consent model to be used to create a Call instance.

        You should use the edc_consent RequiresConsentMixin on the scheduling and unscheduling models to
        avoid hitting the ValueError below when the subject is not consented."""
        consent = self.consent(instance.subject_identifier)
        options = {'subject_identifier': consent.subject_identifier,
                   'first_name': consent.first_name,
                   'initials': consent.initials}
        try:
            consent_foreignkey = getattr(consent, self.consent_model_fk)
            options.update({self.consent_model_fk: consent_foreignkey})
        except AttributeError:
            pass
        return options

    def subject(self, subject_identifier):
        """Return an instance of the subject model."""
        subject = None
        if self.subject_model:
            try:
                subject = self.subject_model.objects.get(
                    subject_identifier=subject_identifier)
            except self.subject_model.DoesNotExist:
                pass
        return subject

    def consent(self, subject_identifier):
        """Return an instance of the consent model or None."""
        consent = None
        if self.consent_model:
            try:
                consent = self.consent_model.objects.get(
                    subject_identifier=subject_identifier)
            except MultipleObjectsReturned:
                consent = self.consent_model.consent.consent_for_period(
                    subject_identifier, get_utcnow())
            except self.consent_model.DoesNotExist as e:
                raise ValueError(
                    'ModelCaller \'{}\' is configured to require a consent for subject \'{}\'. '
                    'Got \'{}\''.format(self.label, subject_identifier, str(e)))
        return consent

    def schedule_call(self, instance, scheduled=None):
        """Schedules a call by creating a new call instance and creates the corresponding Log instance.

        `instance` is a start_model instance"""
        if self.consent_model:
            options = self.personal_details_from_consent(instance)
        else:
            options = self.personal_details_from_subject(instance)
        call = self.call_model.objects.create(
            scheduled=scheduled or date.today(),
            label=self.label,
            repeats=self.repeats,
            **options)
        self.log_model.objects.create(
            call=call,
            locator_information=self.get_locator(instance))

    def unschedule_call(self, subject_identifier):
        """Unschedules any calls for this subject and model caller.

        `instance` is a stop_model instance"""
        self.call_model.objects.filter(
            subject_identifier=subject_identifier,
            label=self.label).exclude(
                call_status=CLOSED).update(
                    call_status=CLOSED,
                    auto_closed=True)

    def schedule_next_call(self, call, scheduled_date=None):
        """Schedules the next call if either scheduled_date is provided or can be calculated."""
        scheduled_date = scheduled_date or self.get_next_scheduled_date(
            call.call_datetime)
        if scheduled_date:
            self.schedule_call(call, scheduled_date)

    def get_next_scheduled_date(self, reference_date):
        """Returns the next scheduled date or None based on the interval.

        TODO: This needs to be a bit more sophisticated to avoid holidays, weekends, etc."""
        scheduled_date = None
        if self.interval == DAILY:
            scheduled_date = reference_date + relativedelta(days=+1)
        elif self.interval == WEEKLY:
            scheduled_date = reference_date + \
                relativedelta(days=+1, weekday=reference_date.weekday())
        elif self.interval == MONTHLY:
            scheduled_date = reference_date + \
                relativedelta(months=+1, weekday=reference_date.weekday())
        else:
            pass
        return scheduled_date

    def update_call_from_log(self, call, log_entry, commit=True):
        """Updates the call_model instance with information from the log entry
        for this subject and model caller.

        Only updates call if this is the most recent log_entry."""
        log_entries = self.log_entry_model.objects.filter(
            log=log_entry.log).order_by('-call_datetime')
        if log_entry.pk == log_entries[0].pk:
            call = self.call_model.objects.get(pk=call.pk)
            if call.call_status == CLOSED:
                raise ValidationError(
                    'Call is closed. Perhaps catch this in the form.')
            call.call_outcome = '. '.join(log_entry.outcome)
            call.call_datetime = log_entry.call_datetime
            call.call_attempts = log_entries.count()
            if log_entry.may_call == NO or log_entry.survival_status == DEAD:
                if log_entry.survival_status == DEAD:
                    call.call_outcome = 'Deceased. ' + \
                        (call.call_outcome or '')
                call.call_status = CLOSED
            else:
                call.call_status = OPEN_CALL
                if log_entry.appt == YES and log_entry.appt_date:
                    call.call_status = CLOSED
            call.modified = log_entry.modified
            call.user_modified = log_entry.user_modified
            if commit:
                call.save()

    def appointment_handler(self, call, log_entry):
        """Called by LogEntry post_save signal."""
        if self.appointment_model:
            self.appointment_model.objects.create(
                appt_date=log_entry.appt_date,
                appt_location=log_entry.appt_location,
                appt_status=NEW_CALL,
            )

    def get_locator(self, instance):
        """Returns the locator instance as a formatted string."""
        locator_str = ''
        if self.locator_model:
            locator_filter = self.locator_filter or 'subject_identifier'
            options = {locator_filter: instance.subject_identifier}
            try:
                locator = self.locator_model.objects.get(**options)
            except self.locator_model.DoesNotExist:
                locator_str = 'locator not found.'
            else:
                for fname in self.locator_model._meta.get_fields():
                    value = getattr(locator, fname.name)
                    if not type(value) == str:
                        value = str(value)
                    locator_str += value + ' '
                locator_str = locator_str[:-1]
        return locator_str

    def get_value(self, instance, attr):
        try:
            value = getattr(instance, attr)
        except AttributeError:
            value = None
        return value
