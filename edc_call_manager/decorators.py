def register(model, **kwargs):
    """
    Registers the given model(s) classes and wrapped ModelAdmin class with
    admin site:

    @register(Author)
    class AuthorAdmin(admin.ModelAdmin):
        pass

    A kwarg of `site` can be passed as the admin site, otherwise the default
    admin site will be used.
    """
    from edc_call_manager.model_caller import ModelCaller
    from edc_call_manager.caller_site import site_model_callers

    def _model_caller_wrapper(caller_class):

        if not issubclass(caller_class, ModelCaller):
            raise ValueError('Wrapped class must subclass ModelAdmin.')

        site_model_callers.register(model, caller_class=caller_class)

        return caller_class
    return _model_caller_wrapper
