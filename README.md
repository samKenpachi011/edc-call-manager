# edc-call-manager
Manage contacting subjects

For example, contact all subjects to complete a revised consent, study closure, etc.


The model_caller can be configured to schedule a call when one model is created and t unschedule the call when another model is created. For example, we need to call expecting mothers weekly until they deliver. We enroll them antenatally by completing the AnteNatalEnrollment form (model). ModelCaller will schedule a call. When the mother delivers we complete the PostNatalEnrollment form (model) and ModelCaller cancels the currently scheduled call.

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


	@register(AnteNatalEnrollment)
	class AnteNatlModelCaller(ModelCaller):
	    label = 'My test caller'
	    unscheduling_model = PostNatalEnrollment
	    interval = WEEKLY

