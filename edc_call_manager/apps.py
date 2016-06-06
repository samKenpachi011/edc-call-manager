import sys
from django.apps import AppConfig

from edc_call_manager.caller_site import site_model_callers


class CallManagerAppConfig(AppConfig):
    name = 'call_manager'
    verbose_name = 'Call Manager'

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        site_model_callers.autodiscover()
