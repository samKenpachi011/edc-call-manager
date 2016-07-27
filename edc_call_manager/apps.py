import sys

from django.apps import AppConfig

from .caller_site import site_model_callers


class EdcCallManagerAppConfig(AppConfig):
    name = 'edc_call_manager'
    verbose_name = 'Call Manager'
    app_label = 'edc_call_manager'  # app_label for models Call, Log, LogEntry if not default

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        site_model_callers.autodiscover()
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
