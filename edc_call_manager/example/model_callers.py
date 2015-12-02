from edc_call_manager.model_caller import ModelCaller, WEEKLY
from edc_call_manager.decorators import register

from .models import TestStartModel, TestStopModel, Consent, Locator


@register(TestStartModel)
class RepeatingTestModelCaller(ModelCaller):

    consent_model = Consent
    locator_model = Locator
    interval = WEEKLY
    label = 'My test caller'
    unscheduling_model = TestStopModel
