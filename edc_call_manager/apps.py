import sys

from datetime import datetime
from dateutil.tz import gettz

from django.apps import AppConfig as DjangoAppConfig
from django.apps import apps as django_apps
from edc_protocol.apps import AppConfig as BaseEdcProtocolAppConfig


class AppConfig(DjangoAppConfig):
    name = 'edc_call_manager'
    verbose_name = 'Call Manager'
    app_label = 'edc_call_manager'  # app_label for models Call, Log, LogEntry if not default
    namespace = 'edc-call-manager'

    def ready(self):
        from edc_call_manager import signals
        from edc_call_manager.caller_site import site_model_callers
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        sys.stdout.write(' * call models are in app {}.\n'.format(self.app_label))
        site_model_callers.autodiscover()
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))

    @property
    def call_model(self):
        return django_apps.get_model(self.app_label, 'call')

    @property
    def log_model(self):
        return django_apps.get_model(self.app_label, 'log')

    @property
    def log_entry_model(self):
        return django_apps.get_model(self.app_label, 'logentry')


class EdcProtocolAppConfig(BaseEdcProtocolAppConfig):
    protocol = 'BHP012'
    protocol_name = 'Edc Call manager'
    protocol_number = '012'
    protocol_title = ''
    study_open_datetime = datetime(
        2016, 4, 1, 0, 0, 0, tzinfo=gettz('UTC'))
    study_close_datetime = datetime(
        2020, 12, 1, 0, 0, 0, tzinfo=gettz('UTC'))
