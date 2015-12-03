import copy

from django.conf import settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule


class AlreadyRegistered(Exception):
    pass


class CallerSite:

    def __init__(self):
        self._registry = {}
        self.reset_registry()

    @property
    def scheduling_models(self):
        return self._registry['scheduling_models']

    @property
    def unscheduling_models(self):
        return self._registry['unscheduling_models']

    @property
    def model_callers(self):
        return self._registry['model_callers']

    def register(self, model, caller_class):

        if model not in self.scheduling_models:
            caller = caller_class(model)
            self.scheduling_models.update({model: caller})
            self.model_callers.update({caller.label: caller})
            if caller.unscheduling_model:
                try:
                    self.unscheduling_models[caller.unscheduling_model].append(model)
                except KeyError:
                    self.unscheduling_models[caller.unscheduling_model] = [model]
        else:
            raise AlreadyRegistered('ModelCaller is already registered for model {}.'.format(model))

    def unregister(self, model):
        del self._registry['scheduling_models'][model]

    def reset_registry(self):
        self._registry = dict(scheduling_models={}, unscheduling_models={}, model_callers={})

    def get_model_caller(self, model):
        try:
            model_caller = self.scheduling_models[model]
        except KeyError:
            model_caller = None
        return model_caller

    def schedule_calls(self, model, instance):
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
                    break
                except KeyError:
                    pass
        except KeyError:
            pass

    def schedule_next_call(self, call):
        model_caller = self._registry['model_callers'].get(call.label)
        model_caller.schedule_next_call(call)

    def autodiscover(self):
        """ Autodiscover rules from a model_callers module."""
        for app in settings.INSTALLED_APPS:
            mod = import_module(app)
            try:
                before_import_registry = copy.copy(site_model_callers._registry)
                import_module('%s.model_callers' % app)
            except:
                site_model_callers._registry = before_import_registry
                if module_has_submodule(mod, 'model_callers'):
                    raise

site_model_callers = CallerSite()
