import sys

from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'edc_call_manager'
    verbose_name = 'Call Manager'
    app_label = 'edc_call_manager'  # app_label for models Call, Log, LogEntry if not default

    def ready(self):
        from .caller_site import site_model_callers
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        site_model_callers.autodiscover()
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
