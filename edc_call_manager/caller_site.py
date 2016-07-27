import copy
import sys

from django.apps import apps as django_apps
from django.core.management.color import color_style
from django.utils.module_loading import import_module
from django.utils.module_loading import module_has_submodule

from .exceptions import ModelCallerError
from .constants import style


class AlreadyRegistered(Exception):
    pass


class CallerSite:

    def __init__(self):
        self._registry = {}
        self.reset_registry()
        self.style = color_style()

    @property
    def start_models(self):
        """Return a dictionary of models used to schedule or 'start" a call or sequence of calls."""
        return self._registry['start_models']

    @property
    def stop_models(self):
        """Return a dictionary of models used to 'close' a call or 'stop' a sequence of calls."""
        return self._registry['stop_models']

    @property
    def model_callers(self):
        return self._registry['model_callers']

    def register(self, caller_class, start_model, stop_model=None, verbose=None):
        verbose = True if verbose is None else verbose
        if start_model not in self.start_models:
            if verbose:
                sys.stdout.write(' * registered model caller \'{}\'\n'.format(str(caller_class)))
            caller = caller_class(start_model, stop_model)
            # self.verify_model(model, caller)
            self.start_models.update({start_model: caller})
            self.model_callers.update({caller.label: caller})
            if stop_model:
                if stop_model in self.stop_models:
                    sys.stdout.write(style.NOTICE(
                        '   Warning: more than one model caller uses model '
                        '\'{}\' to unschedule calls.\n'.format(stop_model._meta.label_lower)))
                try:
                    self.stop_models[stop_model].append(start_model)
                except KeyError:
                    self.stop_models[stop_model] = [start_model]
        else:
            raise AlreadyRegistered(
                'A ModelCaller is already registered with model \'{}\'.'.format(start_model._meta.label_lower))

    def unregister(self, model, caller_):
        """ Unregister this model caller and it's start and stop models."""
        # TODO: this does not completely reset
        del self._registry['start_models'][model]

    def verify_model(self, model, caller):
        """Confirm model has required FK."""
        if ''.join(caller.call_model_fk.split('_')) == model._meta.model_name:
            pass
        else:
            try:
                getattr(model, caller.call_model_fk)
            except AttributeError as e:
                raise ModelCallerError(
                    'Model Caller was registered with model \'{}\'. Model requires '
                    'FK to \'{}\'. Got {}'.format(
                        model, caller.call_model_fk, str(e)))
        if caller.unscheduling_model:
            try:
                getattr(caller.unscheduling_model, caller.call_model_fk)
            except AttributeError as e:
                raise ModelCallerError(
                    'Model Caller was registered with unscheduling model \'{}\'. Model requires '
                    'FK to \'{}\'. Got {}'.format(
                        caller.unscheduling_model, caller.call_model_fk, str(e)))

    def reset_registry(self):
        self._registry = dict(start_models={}, stop_models={}, model_callers={})

    def get_model_caller(self, param):
        """Find and return a model caller class.

        param: either a "start" model class or model_caller label."""

        try:
            model = django_apps.get_model(*param)
        except (LookupError, TypeError, AttributeError):
            model = param
        try:
            model_caller = self.start_models[model]
        except KeyError:
            model_caller = None
        if not model_caller:
            try:
                model_caller = self.model_callers[param]
            except KeyError:
                model_caller = None
        return model_caller

    def schedule_calls(self, model, instance):
        """Schedule a call, e.g. create a Call instance, if the model is registered as a start model."""
        try:
            model_caller = self.start_models[model]
            model_caller.schedule_call(instance)
        except KeyError:
            pass

    def unschedule_calls(self, model, instance):
        """Unschedule a call(s) if model is a stop model."""
        try:
            start_models = self.stop_models[model]
            for start_model in start_models:
                try:
                    model_caller = self.start_models[start_model]
                    model_caller.unschedule_call(instance.subject_identifier)
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
