import sys

from datetime import datetime
from dateutil.tz import gettz

from django.apps import AppConfig as DjangoAppConfig
from django.apps import apps as django_apps
from edc_protocol.apps import AppConfig as BaseEdcProtocolAppConfig


class AppConfig(DjangoAppConfig):
    name = 'edc_call_manager'
    verbose_name = 'EDC Call Manager'
    admin_site_name = 'edc_call_manager_admin'

    def ready(self):
        from edc_call_manager import signals
        from edc_call_manager.caller_site import site_model_callers
        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        sys.stdout.write(f' * call models are in app {self.name}.\n')
        site_model_callers.autodiscover()
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')

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
