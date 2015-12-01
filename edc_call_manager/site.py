class AlreadyRegistered(Exception):
    pass


class CallerSite:

    scheduling_models = {}
    unscheduling_models = {}
    model_callers = {}

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

site = CallerSite()
