from datetime import date
from django.db import models
from django.core.validators import RegexValidator

from edc_base.audit_trail import AuditTrail
from edc_base.encrypted_fields import EncryptedTextField, FirstnameField
from edc_base.model.fields import OtherCharField
from edc_base.model.models import BaseUuidModel
from edc_base.model.validators import datetime_not_future, datetime_not_before_study_start, date_is_future
from edc_constants.choices import YES_NO_UNKNOWN, TIME_OF_DAY, TIME_OF_WEEK, YES_NO
from edc_constants.constants import YES, CLOSED, OPEN, NEW

from .choices import CONTACT_TYPE, APPT_GRADING, APPT_LOCATIONS


class Call(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)

    label = models.CharField(max_length=25)

    scheduled = models.DateField(
        default=date.today())

    repeats = models.BooleanField(
        default=False)

    last_called = models.DateTimeField(
        null=True,
        editable=False,
        help_text='last call datetime updated by call log entry',
    )

    first_name = FirstnameField(
        verbose_name='First name',
        editable=False,
    )

    initials = models.CharField(
        verbose_name='Initials',
        max_length=3,
        editable=False,
    )

    consent_datetime = models.DateTimeField(
        verbose_name="Consent date and time",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future, ],
        help_text="From Subject Consent.",
        null=True,
    )

    call_attempts = models.IntegerField(
        default=0)

    call_outcome = models.TextField(
        max_length=150,
        null=True,
    )

    call_status = models.CharField(
        max_length=15,
        choices=(
            (NEW, 'New'),
            (OPEN, 'Open'),
            (CLOSED, 'Closed'),
        ),
        default=NEW,
    )

    history = AuditTrail()

    def __str__(self):
        return '{} {}'.format(
            self.first_name,
            self.initials,
            self.call_status,
        )

    class Meta:
        app_label = 'edc_call_manager'


class Log(BaseUuidModel):

    call = models.ForeignKey(Call)

    locator_information = EncryptedTextField(
        help_text='This information has been imported from the previous locator. You may update as required.')

    contact_notes = EncryptedTextField(
        null=True,
        blank=True,
        help_text='')

    history = AuditTrail()

    def __str__(self):
        return str(self.call)

    class Meta:
        app_label = 'edc_call_manager'


class LogEntry (BaseUuidModel):

    log = models.ForeignKey(Log)

    call_datetime = models.DateTimeField()

    invalid_numbers = models.CharField(
        verbose_name='Indicate any invalid numbers dialed from the locator information above?',
        max_length=50,
        validators=[RegexValidator(
            regex=r'^[0-9]{7,8}(,[0-9]{7,8})*$',
            message='Only enter contact numbers separated by commas. No spaces and no trailing comma.'), ],
        null=True,
        blank=True,
        help_text='Separate by comma (,).'
    )

    contact_type = models.CharField(
        max_length=15,
        choices=CONTACT_TYPE,
        help_text='If no contact made. STOP. Save form.'
    )

    time_of_week = models.CharField(
        verbose_name='Time of week when participant will be available',
        max_length=25,
        choices=TIME_OF_WEEK,
        blank=True,
        null=True,
        help_text=""
    )

    time_of_day = models.CharField(
        verbose_name='Time of day when participant will be available',
        max_length=25,
        choices=TIME_OF_DAY,
        blank=True,
        null=True,
        help_text=""
    )

    appt = models.CharField(
        verbose_name='Is the participant willing to schedule an appointment',
        max_length=7,
        choices=YES_NO_UNKNOWN,
        null=True,
        blank=True,
    )

    appt_date = models.DateField(
        verbose_name="Appointment Date",
        validators=[date_is_future],
        null=True,
        blank=True,
        help_text="This can only come from the participant."
    )

    appt_grading = models.CharField(
        verbose_name='Is this appointment...',
        max_length=25,
        choices=APPT_GRADING,
        null=True,
        blank=True,
    )

    appt_location = models.CharField(
        verbose_name='Appointment location',
        max_length=50,
        choices=APPT_LOCATIONS,
        null=True,
        blank=True,
    )

    appt_location_other = OtherCharField(
        verbose_name='Appointment location',
        max_length=50,
        null=True,
        blank=True,
    )

    delivered = models.NullBooleanField(
        default=False,
        editable=False)

    call_again = models.CharField(
        verbose_name='Call the participant again?',
        max_length=10,
        choices=YES_NO,
        default=YES,
    )

    history = AuditTrail()

    class Meta:
        app_label = 'edc_call_manager'
