from itertools import chain

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.edit import UpdateView, DeleteView, CreateView

from edc_base.modelform.mixins import AuditFieldsMixin
from edc_base.utils.age import formatted_age
from edc_call_manager.constants import DIRECT_CONTACT, INDIRECT_CONTACT, NO_CONTACT
from edc_constants.constants import NO, CLOSED

from .caller_site import site_model_callers
from .forms import LogEntryForm

LogEntry = django_apps.get_model('call_manager', 'logentry')


class CallSubjectViewMixin:

    template_name = 'call_subject.html'
    call_manager_app = 'call_manager'
    form_class = LogEntryForm
    show_instructions = True
    instructions = 'Complete the form as required.'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CallSubjectViewMixin, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('call_manager_admin:call_manager_call_changelist')

    def get_form_kwargs(self):
        kwargs = super(CallSubjectViewMixin, self).get_form_kwargs()
        kwargs['initial'].update({'log': self.log})
        return kwargs

    def get_object(self):
        return self.model.objects.get(pk=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject_identifier = self.log.call.subject_identifier
        call_status = self.log.call.get_call_status_display()
        context.update(
            title=settings.PROJECT_TITLE,
            project_name=settings.PROJECT_TITLE,
            instructions=self.instructions,
            show_instructions=self.show_instructions,
            caller_app=self.kwargs.get('caller_app'),
            caller_model=self.kwargs.get('caller_model'),
            contact_information=self.get_contact_information(),
            subject_identifier=subject_identifier,
            call_status=call_status,
            log_pk=str(self.kwargs.get('log_pk')),
            next_url=self.get_success_url(),
            label='call',
            **dict(chain.from_iterable(
                d.items() for d in (self.demographics, self.contact_history, self.appointments))),
        )
        return context

    @property
    def log(self):
        return self.caller.log_model.objects.get(pk=self.kwargs.get('log_pk'))

    @property
    def caller(self):
        return site_model_callers.get_model_caller(
            (self.kwargs.get('caller_app'), self.kwargs.get('caller_model')))

    @property
    def demographics(self):
        return {'name': '{} {}'.format(self.log.call.subject.first_name, self.log.call.subject.last_name),
                'first_name': self.log.call.subject.first_name,
                'last_name': self.log.call.subject.last_name,
                'gender': self.log.call.subject.get_gender_display(),
                'dob': self.log.call.subject.dob,
                'age': formatted_age(self.log.call.subject.dob)}

    @property
    def appointments(self):
        appointments = []
        appt = {}
        history = self.model.objects.filter(log=self.log).order_by('-call_datetime')
        for obj in history:
            try:
                appt = {
                    'appt_date': obj.appt_date.strftime('%Y-%m-%d'),
                    'appt_grading': obj.get_appt_grading_display(),
                }
            except AttributeError:
                pass
        appointments.append(appt)
        return {'appointments': appointments}

    @property
    def locator_model(self):
        return self.caller.locator_model

    @property
    def locator_filter(self):
        return self.caller.locator_filter

    def get_contact_information(self):
        try:
            contact_information = self.locator_model.objects.get(
                **{self.locator_filter: self.log.call.subject.subject_identifier}).to_dict()
        except self.locator_model.DoesNotExist:
            contact_information = None
        return contact_information

    @property
    def contact_history(self):
        history = self.model.objects.filter(log=self.log).order_by('-call_datetime')
        contact_history = {
            'attempts': history.filter(log=self.log).count(),
            'direct_contact': history.filter(log=self.log, contact_type=DIRECT_CONTACT).count(),
            'indirect_contact': history.filter(log=self.log, contact_type=INDIRECT_CONTACT).count(),
            'no_contact': history.filter(log=self.log, contact_type=NO_CONTACT).count(),
            'do_not_call': self.do_not_call(history),
            'call_closed': self.call_closed(history),
            'contact_history': history,
        }
        return contact_history

    def do_not_call(self, history):
        try:
            history.get(may_call=NO)
            do_not_call = True
        except MultipleObjectsReturned:
            do_not_call = True
        except ObjectDoesNotExist:
            do_not_call = False
        return do_not_call

    def call_closed(self, history):
        try:
            history.get(log__call__call_status=CLOSED)
            call_closed = True
        except MultipleObjectsReturned:
            call_closed = True
        except ObjectDoesNotExist:
            call_closed = False
        return call_closed


class CallSubjectCreateView(CallSubjectViewMixin, AuditFieldsMixin, CreateView):

    model = LogEntry

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['label'] = 'Add Call Log Entry'
        return context

    def form_valid(self, form):
        form.instance.log = self.log
        return super(CallSubjectCreateView, self).form_valid(form)


class CallSubjectUpdateView(CallSubjectViewMixin, AuditFieldsMixin, UpdateView):

    model = LogEntry

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['label'] = 'Change Call Log Entry'
        return context

    def form_valid(self, form):
        form.instance.log = self.log
        return super(CallSubjectUpdateView, self).form_valid(form)


class CallSubjectDeleteView(CallSubjectViewMixin, AuditFieldsMixin, DeleteView):

    model = LogEntry
    success_url = reverse_lazy('call-subject-delete')
