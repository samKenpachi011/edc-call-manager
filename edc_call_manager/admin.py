from django.contrib import admin
from django.contrib.admin import AdminSite
from django.apps import apps as django_apps

from edc_base.modeladmin.mixins import ModelAdminBasicMixin, ModelAdminChangelistModelButtonMixin
from edc_constants.constants import NEW, OPEN

from .actions import call_participant


class CallManagerAdminSite(AdminSite):
    """
    For example:
        add to urls:
            url(r'^call_manager/', call_manager_admin.urls),
        then:
            >>> reverse('call_manager_admin:edc_call_manager_call_add')
            '/call_manager/edc_call_manager/call/add/'
    """
    site_header = 'Call Manager'
    site_title = 'Call Manager'
    index_title = 'Call Manager Administration'
    site_url = '/'
call_manager_admin = CallManagerAdminSite(name='call_manager_admin')


class ModelAdminCallMixin(ModelAdminChangelistModelButtonMixin, ModelAdminBasicMixin):

    subject_app = 'registration'
    subject_model = 'registeredsubject'

    date_hierarchy = 'modified'

    actions = [call_participant]

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

    mixin_search_fields = ('subject_identifier', 'initials')

    def call_button(self, obj):
        Log = django_apps.get_model('call_manager', 'log')
        log = Log.objects.get(call=obj)
        if obj.call_status == NEW:
            change_label = 'New&nbsp;Call'.format(obj.call_attempts)
        elif obj.call_status == OPEN:
            change_label = 'Open&nbsp;Call'.format(obj.call_attempts)
        else:
            change_label = 'Closed&nbsp;Call'
        return self.change_button(
            'call-subject-add', (self.subject_app, self.subject_model, str(log.pk), ),
            label=change_label, namespace='call_manager')
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

    redirect_app_label = 'call_manager'
    redirect_model_name = 'call'
    redirect_search_field = 'call__subject_identifier'
    redirect_namespace = 'call_manager_admin'

    mixin_fields = ("call", 'locator_information', 'contact_notes')

    readonly_fields = ('call', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "call":
            Call = django_apps.get_model('call_manager', 'call')
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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "log":
            Log = django_apps.get_model('call_manager', 'Log')
            kwargs["queryset"] = Log.objects.filter(id__exact=request.GET.get('call_log', 0))
        return super(ModelAdminLogEntryMixin, self).formfield_for_foreignkey(db_field, request, **kwargs)
