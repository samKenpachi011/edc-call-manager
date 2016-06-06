import copy
import sys

from django.apps import apps as django_apps
from django.core.management.color import color_style
from django.utils.module_loading import import_module
from django.utils.module_loading import module_has_submodule
from edc_call_manager.exceptions import ModelCallerError
from edc_call_manager.constants import style


class AlreadyRegistered(Exception):
    pass


class CallerSite:

    def __init__(self):
        self._registry = {}
        self.reset_registry()
        self.style = color_style()

    @property
    def scheduling_models(self):
        return self._registry['scheduling_models']

    @property
    def unscheduling_models(self):
        return self._registry['unscheduling_models']

    @property
    def model_callers(self):
        return self._registry['model_callers']

    def register(self, model, caller_class, verbose=None):
        verbose = True if verbose is None else verbose
        if model not in self.scheduling_models:
            if verbose:
                sys.stdout.write(' * registered model caller \'{}\'\n'.format(str(caller_class)))
            caller = caller_class(model)
            self.verify_model(model, caller)
            self.scheduling_models.update({model: caller})
            self.model_callers.update({caller.label: caller})
            if caller.unscheduling_model:
                if caller.unscheduling_model in self.unscheduling_models:
                    sys.stdout.write(style.NOTICE(
                        '   Warning: more than one model caller uses unscheduling model '
                        '\'{}\'.\n'.format(caller.unscheduling_model._meta.object_name)))
                try:
                    self.unscheduling_models[caller.unscheduling_model].append(model)
                except KeyError:
                    self.unscheduling_models[caller.unscheduling_model] = [model]
        else:
            raise AlreadyRegistered('ModelCaller is already registered for model {}.'.format(model))

    def unregister(self, model):
        del self._registry['scheduling_models'][model]

    def verify_model(self, model, caller):
        """Confirm model has required FK."""
        try:
            getattr(model, caller.call_model_subject_foreignkey)
        except AttributeError as e:
            raise ModelCallerError(
                'Model Caller was registered with model \'{}\'. Model requires '
                'FK to \'{}\'. Got {}'.format(
                    model, caller.call_model_subject_foreignkey, str(e)))
        if caller.unscheduling_model:
            try:
                getattr(caller.unscheduling_model, caller.call_model_subject_foreignkey)
            except AttributeError as e:
                raise ModelCallerError(
                    'Model Caller was registered with unscheduling model \'{}\'. Model requires '
                    'FK to \'{}\'. Got {}'.format(
                        caller.unscheduling_model, caller.call_model_subject_foreignkey, str(e)))

    def reset_registry(self):
        self._registry = dict(scheduling_models={}, unscheduling_models={}, model_callers={})

    def get_model_caller(self, model):
        try:
            model = django_apps.get_model(*model)
        except (LookupError, TypeError, AttributeError):
            pass
        try:
            model_caller = self.scheduling_models[model]
        except KeyError:
            model_caller = None
        return model_caller

    def schedule_calls(self, model, instance):
        """Schedule a call, e.g. create a Call instance, if the model is registered."""
        try:
            model_caller = self.scheduling_models[model]
            model_caller.schedule_call(instance)
        except KeyError:
            pass

    def unschedule_calls(self, model, instance):
        try:
            scheduling_models = self.unscheduling_models[model]
            for scheduling_model in scheduling_models:
                try:
                    model_caller = self.scheduling_models[scheduling_model]
                    model_caller.unschedule_call(instance)
                except KeyError:
                    pass
        except KeyError:
            pass

    def schedule_next_call(self, call):
        try:
            model_caller = self._registry['model_callers'].get(call.label)
            model_caller.schedule_next_call(call)
        except AttributeError as e:
            if 'object has no attribute \'label\'' not in str(e):
                raise AttributeError(e)

    def update_call_from_log(self, call, log_entry=None):
        model_caller = self._registry['model_callers'].get(call.label)
        model_caller.update_call_from_log(call, log_entry)

    def autodiscover(self, module_name=None):
        """ Autodiscover rules from a model_callers module."""
        module_name = module_name or 'model_callers'
        sys.stdout.write(' * checking for site {} ...\n'.format(module_name))
        for app in django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(site_model_callers._registry)
                    import_module('{}.{}'.format(app, module_name))
                except:
                    site_model_callers._registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise
            except ImportError:
                pass

site_model_callers = CallerSite()
