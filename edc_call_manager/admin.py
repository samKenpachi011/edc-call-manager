from django.apps import apps as django_apps
from django.contrib import admin

from edc_base.modeladmin.mixins import (
    ModelAdminBasicMixin, ModelAdminChangelistModelButtonMixin,
    ModelAdminFormAutoNumberMixin, ModelAdminFormInstructionsMixin)
from simple_history.admin import SimpleHistoryAdmin

from .admin_site import edc_call_manager_admin
from .constants import NEW_CALL, OPEN_CALL
from .models import Call, Log, LogEntry

app_config = django_apps.get_app_config('edc_call_manager')


class BaseModelAdmin(ModelAdminFormInstructionsMixin, ModelAdminFormAutoNumberMixin):
    list_per_page = 10
    date_hierarchy = 'modified'
    empty_value_display = '-'


class ModelAdminCallMixin(ModelAdminChangelistModelButtonMixin, ModelAdminBasicMixin):

    date_hierarchy = 'modified'

    mixin_fields = (
        'call_attempts',
        'call_status',
        'call_outcome',
    )

    mixin_radio_fields = {'call_status': admin.VERTICAL}

    list_display_pos = None
    mixin_list_display = (
        'subject_identifier',
        'call_button',
        'call_attempts',
        'call_outcome',
        'scheduled',
        'label',
        'first_name',
        'initials',
        'user_created',
    )

    mixin_list_filter = (
        'call_status',
        'call_attempts',
        'modified',
        'hostname_created',
        'user_created',
    )

    mixin_readonly_fields = (
        'call_attempts',
    )

    mixin_search_fields = ('subject_identifier', 'initials', 'label')

    def call_button(self, obj):
        Log = django_apps.get_model(app_config.app_label, 'log')
        log = Log.objects.get(call=obj)
        args = (log.call.label, str(log.pk))
        if obj.call_status == NEW_CALL:
            change_label = 'New&nbsp;Call'.format(obj.call_attempts)
        elif obj.call_status == OPEN_CALL:
            change_label = 'Open&nbsp;Call'.format(obj.call_attempts)
        else:
            change_label = 'Closed&nbsp;Call'
        return self.change_button(
            'call-subject-add', args, label=change_label, namespace=app_config.namespace)
    call_button.short_description = 'call'


class ModelAdminLogEntryInlineMixin(object):

    instructions = [
        'Please read out to participant. "We hope you have been well since our visit last year. '
        'As a member of this study, it is time for your revisit in which we will ask you '
        'some questions and perform some tests."',
        'Please read out to contact other than participant. (Note: You may NOT disclose that the '
        'participant is a member of the this study). "We would like to contact a participant '
        '(give participant name) who gave us this number as a means to contact them. Do you know '
        'how we can contact this person directly? This may be a phone number or a physical address.']

    model = None
    max_num = 3
    extra = 1

    fields = (
        'call_datetime',
        'contact_type',
        'time_of_week',
        'time_of_day',
        'appt',
        'appt_reason_unwilling',
        'appt_reason_unwilling_other',
        'appt_date',
        'appt_grading',
        'appt_location',
        'appt_location_other',
        'may_call',
    )

    radio_fields = {
        "contact_type": admin.VERTICAL,
        "time_of_week": admin.VERTICAL,
        "time_of_day": admin.VERTICAL,
        "appt": admin.VERTICAL,
        "appt_reason_unwilling": admin.VERTICAL,
        "appt_grading": admin.VERTICAL,
        "appt_location": admin.VERTICAL,
        "may_call": admin.VERTICAL,
    }


class ModelAdminLogMixin(ModelAdminBasicMixin):

    instructions = [
        '<h5>Please read out to participant:</h5> "We hope you have been well since our visit last year. '
        'As a member of this study, it is time for your revisit in which we will ask you '
        'some questions and perform some tests."',
        '<h5>Please read out to contact other than participant:</h5> (<B>IMPORTANT:</B> You may NOT disclose that the '
        'participant is a member of the this study).<BR>"We would like to contact a participant '
        '(give participant name) who gave us this number as a means to contact them. Do you know '
        'how we can contact this person directly? This may be a phone number or a physical address.']

    redirect_app_label = app_config.app_label
    redirect_model_name = 'call'
    redirect_search_field = 'call__subject_identifier'
    redirect_namespace = 'edc_call_manager_admin'

    mixin_fields = ("call", 'locator_information', 'contact_notes')

    readonly_fields = ('call', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "call":
            Call = django_apps.get_model(app_config.app_label, 'call')
            try:
                call = Call.objects.get(pk=request.GET.get('call'))
                kwargs["queryset"] = [call]
            except Call.DoesNotExist:
                pass
        return super(ModelAdminLogMixin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ModelAdminLogEntryMixin(object):

    date_hierarchy = 'appt_date'
    instructions = [
        'Please read out to participant. "We hope you have been well since our visit last year. '
        'As a member of this study, it is time for your revisit in which we will ask you '
        'some questions and perform some tests."',
        'Please read out to contact other than participant. (Note: You may NOT disclose that the '
        'participant is a member of this study). "We would like to contact a participant '
        '(give participant name) who gave us this number as a means to contact them. Do you know '
        'how we can contact this person directly? This may be a phone number or a physical address.']

    fields = (
        'log',
        'call_reason',
        'call_datetime',
        'contact_type',
        'time_of_week',
        'time_of_day',
        'appt',
        'appt_reason_unwilling',
        'appt_reason_unwilling_other',
        'appt_date',
        'appt_grading',
        'appt_location',
        'appt_location_other',
        'may_call',
    )

    radio_fields = {
        "contact_type": admin.VERTICAL,
        "time_of_week": admin.VERTICAL,
        "time_of_day": admin.VERTICAL,
        "appt": admin.VERTICAL,
        "appt_reason_unwilling": admin.VERTICAL,
        "appt_grading": admin.VERTICAL,
        "appt_location": admin.VERTICAL,
        "may_call": admin.VERTICAL,
    }

    list_display = (
        'log',
        'call_datetime',
        'appt',
        'appt_date',
        'may_call',
    )

    list_filter = (
        'call_datetime',
        'appt',
        'appt_date',
        'may_call',
        'created',
        'modified',
        'hostname_created',
        'hostname_modified',
    )

    search_fields = ('id', 'log__call__subject_identifier')

    readonly_fields = ('log', )


if app_config.app_label == 'edc_call_manager':

    @admin.register(Call, site=edc_call_manager_admin)
    class CallAdmin(BaseModelAdmin, ModelAdminCallMixin, SimpleHistoryAdmin):
        pass

    @admin.register(Log, site=edc_call_manager_admin)
    class LogAdmin(BaseModelAdmin, ModelAdminLogMixin, SimpleHistoryAdmin):
        pass

    @admin.register(LogEntry, site=edc_call_manager_admin)
    class LogEntryAdmin(BaseModelAdmin, ModelAdminLogEntryMixin, SimpleHistoryAdmin):
        pass
