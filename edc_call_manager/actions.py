from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect


from .models import Log
# from .utils import update_call_list, add_to_call_list


# def update_call_list_action(modeladmin, request, queryset):
#     update_call_list()
# update_call_list_action.short_description = "Update Call List"


# def add_to_call_list_action(modeladmin, request, queryset):
#     for qs in queryset:
#         add_to_call_list(qs)
# add_to_call_list_action.short_description = "Add to Call List"


def call_participant(modeladmin, request, queryset):
    """
    Redirects to a new or existing Log.
    """
    call = queryset[0]
    log = Log.objects.get(call=call)
#    locator_information=SubjectLocator.objects.previous(household_member).formatted_locator_information
    change_url = ('{}?next={}&q={}').format(
        reverse("admin:edc_call_manager_log_change", args=(log.pk, )),
        "admin:{}_{}_changelist".format(call._meta.app_label, call._meta.object_name.lower()),
        request.GET.get('q'),)
    return HttpResponseRedirect(change_url)
call_participant.short_description = "Call participant"
