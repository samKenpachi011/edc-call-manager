from django.apps import apps as django_apps
from django import forms

from .admin import call_manager_admin

from edc_base.modelform.mixins import CrispyFormMixin
from edc_constants.constants import CLOSED, OTHER, YES


class LogEntryForm(CrispyFormMixin, forms.ModelForm):

    hidden_fields = ['log']
    use_modeladmin = True
    admin_site = call_manager_admin

    def clean(self):
        cleaned_data = super(LogEntryForm, self).clean()
        log = cleaned_data.get('log')
        if cleaned_data.get('appt_location') == OTHER and not cleaned_data.get('appt_location_other'):
            raise forms.ValidationError('You wrote the appointment location is OTHER, please specify below.')
        if cleaned_data.get('appt') == YES and not cleaned_data.get('appt_date'):
            raise forms.ValidationError('You wrote the participant is willing to make an appointment. Please specify the appointment date.')
        if cleaned_data.get('appt') == YES and not cleaned_data.get('appt_grading'):
            raise forms.ValidationError('You wrote the participant is willing to make an appointment. Please specify if this is a firm appointment date or not.')
        if cleaned_data.get('appt') == YES and not cleaned_data.get('appt_location'):
            raise forms.ValidationError('You wrote the participant is willing to make an appointment. Please specify the appointment location.')
        if log.call.call_status == CLOSED:
            raise forms.ValidationError('This call is closed. You may not add to or change the call log.')
        return cleaned_data

    class Meta:
        model = django_apps.get_model('call_manager', 'logentry')
        fields = '__all__'
