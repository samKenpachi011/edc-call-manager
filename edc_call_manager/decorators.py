def register(model, **kwargs):
    """
    Registers the given model class and wrapped ModelCaller class with
    site_model_callers:

    @register(Antenatal)
    class AntenatalModelCaller(ModelCaller):
        pass
    """
    from edc_call_manager.model_caller import ModelCaller
    from edc_call_manager.caller_site import site_model_callers

    def _model_caller_wrapper(caller_class):

        if not issubclass(caller_class, ModelCaller):
            raise ValueError('Wrapped class must subclass ModelCaller.')

        site_model_callers.register(model, caller_class=caller_class)

        return caller_class
    return _model_caller_wrapper
