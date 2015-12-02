from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect

from .models import Log
from django.contrib import messages
from django.contrib.messages.constants import WARNING


def call_participant(modeladmin, request, queryset):
    """
    Redirects to a new or existing Log.
    """
    if queryset.count() == 1:
        call = queryset[0]
        log = Log.objects.get(call=call)
        change_url = ('{}?next={}&q={}').format(
            reverse("admin:edc_call_manager_log_change", args=(log.pk, )),
            "admin:{}_{}_changelist".format(call._meta.app_label, call._meta.object_name.lower()),
            request.GET.get('q'),)
        return HttpResponseRedirect(change_url)
    else:
        messages.add_message(request, WARNING, 'Please select only one subject to call at a time.')
call_participant.short_description = "Call participant"
