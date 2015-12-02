# edc-call-manager

Configure models to manage scheduling calls to subjects.

For example, contact all subjects to complete a revised consent, study closure, etc.


The model_caller can be configured to schedule a call when one model is created and to unschedule the call when another model is created. For example, we need to call expecting mothers weekly until they deliver. We enroll them antenatally by completing the `AnteNatalEnrollment` form (model). ModelCaller `AnteNatalModelCaller` will schedule a call. When the mother delivers we complete the `PostNatalEnrollment` form (model) and ModelCaller `AnteNatalModelCaller` cancels the currently scheduled call.

	class AnteNatalEnrollment(models.Model):
	
	    subject_identifier = models.CharField(
	        max_length=25)
	
	    subject_date = models.DateField(
	        default=datetime.now())
	
	    class Meta:
	        app_label = 'my_app'


	class PostNatalEnrollment(models.Model):
	
	    subject_identifier = models.CharField(
	        max_length=25)
	
	    subject_date = models.DateField(
	        default=datetime.now())
	
	    class Meta:
	        app_label = 'my_app'

The ModelCaller is declared as follows:

	from edc_call_manager.model_caller import ModelCaller, WEEKLY
	from edc_call_manager.decorators import register

	from .models import MaternalConsent, Locator

	@register(AnteNatalEnrollment)
	class AnteNatalModelCaller(ModelCaller):
	    label = 'Antenatal-to-Postnatal'
	    consent_model = MaternalConsent
	    locator_model = Locator
	    unscheduling_model = PostNatalEnrollment
	    interval = WEEKLY


