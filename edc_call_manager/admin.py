from django.contrib import admin

from edc_base.modeladmin.admin import BaseModelAdmin, BaseStackedInline

from .actions import call_participant
from .models import Log, Call, LogEntry


class CallAdmin(BaseModelAdmin):

    date_hierarchy = 'created'

    actions = [call_participant]

    fields = (
        'call_attempts',
        'call_status',
        'call_outcome',
    )
    radio_fields = {'call_status': admin.VERTICAL}

    list_display = (
        'subject_identifier',
        'scheduled',
        'label',
        'first_name',
        'initials',
        'call_attempts',
        'call_status',
        'call_outcome',
        "consent_datetime",
        'user_created',
    )
    list_filter = (
        'call_attempts',
        'call_status',
        'created',
        'consent_datetime',
        'hostname_created',
        'user_created',
    )

    readonly_fields = (
        'call_attempts',
        # 'antenatal_enrollment',
    )

    search_fields = ('subject_identifier', 'initials')

admin.site.register(Call, CallAdmin)


class LogEntryAdminInline(BaseStackedInline):
    instructions = [
        'Please read out to participant. "We hope you have been well since our visit last year. '
        'As a member of this study, it is time for your revisit in which we will ask you '
        'some questions and perform some tests."',
        'Please read out to contact other than participant. (Note: You may NOT disclose that the '
        'participant is a member of the this study). "We would like to contact a participant '
        '(give participant name) who gave us this number as a means to contact them. Do you know '
        'how we can contact this person directly? This may be a phone number or a physical address.']

    model = LogEntry
    max_num = 3
    extra = 1

    fields = (
        'call_datetime',
        'invalid_numbers',
        'contact_type',
        'time_of_week',
        'time_of_day',
        'appt',
        'appt_date',
        'appt_grading',
        'appt_location',
        'appt_location_other',
        'call_again',
    )

    radio_fields = {
        "contact_type": admin.VERTICAL,
        "time_of_week": admin.VERTICAL,
        "time_of_day": admin.VERTICAL,
        "appt": admin.VERTICAL,
        "appt_grading": admin.VERTICAL,
        "appt_location": admin.VERTICAL,
        "call_again": admin.VERTICAL,
    }


class LogAdmin(BaseModelAdmin):

    instructions = [
        '<h5>Please read out to participant:</h5> "We hope you have been well since our visit last year. '
        'As a member of this study, it is time for your revisit in which we will ask you '
        'some questions and perform some tests."',
        '<h5>Please read out to contact other than participant:</h5> (<B>IMPORTANT:</B> You may NOT disclose that the '
        'participant is a member of the this study).<BR>"We would like to contact a participant '
        '(give participant name) who gave us this number as a means to contact them. Do you know '
        'how we can contact this person directly? This may be a phone number or a physical address.']

    fields = ("call", 'locator_information', 'contact_notes')

    inlines = [LogEntryAdminInline, ]

#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "call":
#             kwargs["queryset"] = Call.objects.filter(id__exact=request.GET.get('household_member', 0))
#         return super(LogAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Log, LogAdmin)


class LogEntryAdmin(BaseModelAdmin):

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
        'call_datetime',
        'invalid_numbers',
        'contact_type',
        'time_of_week',
        'time_of_day',
        'appt',
        'appt_date',
        'appt_grading',
        'appt_location',
        'appt_location_other',
        'call_again',
    )

    radio_fields = {
        "contact_type": admin.VERTICAL,
        "time_of_week": admin.VERTICAL,
        "time_of_day": admin.VERTICAL,
        "appt": admin.VERTICAL,
        "appt_grading": admin.VERTICAL,
        "appt_location": admin.VERTICAL,
        "call_again": admin.VERTICAL,
    }

    list_display = (
        'log',
        'call_datetime',
        'appt',
        'appt_date',
        'call_again',
    )

    list_filter = (
        'call_datetime',
        'appt',
        'appt_date',
        'call_again',
        'created',
        'modified',
        'hostname_created',
        'hostname_modified',
    )

    search_fields = ('call_log__call_list__first_name', 'id')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "log":
            kwargs["queryset"] = Log.objects.filter(id__exact=request.GET.get('call_log', 0))
        return super(LogEntryAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(LogEntry, LogEntryAdmin)
