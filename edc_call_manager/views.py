import copy
import json

from django.apps import apps as django_apps
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView, DeleteView, CreateView

from edc_base.modelform.mixins import AuditFieldsMixin
from edc_base.views.edc_base_view_mixin import EdcBaseViewMixin
from edc_constants.constants import ALIVE

from .view_mixins import CallSubjectViewMixin
from edc_call_manager.caller_site import site_model_callers
import jsonpickle

app_config = django_apps.get_app_config('edc_call_manager')
Call = django_apps.get_model(app_config.app_label, 'call')
Log = django_apps.get_model(app_config.app_label, 'log')
LogEntry = django_apps.get_model(app_config.app_label, 'logentry')


class HomeView(EdcBaseViewMixin, TemplateView):

    template_name = 'edc_call_manager/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'model_callers': site_model_callers.model_callers.values()})
        context.update({'project_name': self.main_app_config.verbose_name + ': ' + 'Call Manager'})
        context.update({'app_label': app_config.app_label})
        context.update({'context': jsonpickle.encode(context)})
        return context


class CallSubjectCreateView(CallSubjectViewMixin, AuditFieldsMixin, CreateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['label'] = 'Add Call Log Entry'
        return context

    def form_valid(self, form):
        form.instance.log = self.log
        form.instance.survival_status = ALIVE
        return super(CallSubjectCreateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(CallSubjectCreateView, self).form_invalid(form)


class CallSubjectUpdateView(CallSubjectViewMixin, AuditFieldsMixin, UpdateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['label'] = 'Change Call Log Entry'
        return context

    def form_valid(self, form):
        form.instance.log = self.log
        form.instance.survival_status = ALIVE
        return super(CallSubjectUpdateView, self).form_valid(form)


class CallSubjectDeleteView(CallSubjectViewMixin, AuditFieldsMixin, DeleteView):

    success_url = reverse_lazy('call-subject-delete')
