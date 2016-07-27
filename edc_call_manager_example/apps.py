from django.apps import AppConfig

from edc_call_manager.apps import EdcCallManagerAppConfig as EdcCallManagerAppConfigParent


class EdcCallManagerExampleAppConfig(AppConfig):
    name = 'edc_call_manager_example'
    institution = 'Example Corp'
    verbose_name = 'Example App'


class EdcCallManagerAppConfig(EdcCallManagerAppConfigParent):
    app_label = 'edc_call_manager_example'
