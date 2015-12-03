# edc-call-manager

Configure models to manage scheduling calls to subjects.

For example, contact all subjects to complete a revised consent, study closure, etc.

## ModelCaller

The `ModelCaller` schedules a call when one model is created and unschedules the call when another model is created. For example, we need to call expecting mothers weekly until they deliver. We enroll them antenatally by completing the `AnteNatalEnrollment` model. Once complete, ModelCaller `AnteNatalFollowUpModelCaller` schedules a call to the mother represented by an instance in the `Call` model. When the mother delivers the `PostNatalEnrollment` model is completed and ModelCaller `AnteNatalModelCaller` cancels any currently scheduled calls managed by the `AnteNatalFollowUpModelCaller`.

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

The `AnteNatalFollowUpModelCaller` ModelCaller is declared as follows:

	from edc_call_manager.model_caller import ModelCaller, WEEKLY
	from edc_call_manager.decorators import register

	from .models import MaternalConsent, Locator

	@register(AnteNatalEnrollment)
	class AnteNatalFollowUpModelCaller(ModelCaller):
	    label = 'Antenatal-to-Postnatal'
	    consent_model = MaternalConsent
	    locator_model = Locator
	    unscheduling_model = PostNatalEnrollment
	    interval = WEEKLY

In the declaration we have included the `consent_model` and the `locator_model`. ModelCaller uses these models to extract personal information on the subject for the research assistant making the follow-up calls. In almost all cases, the subject has been consented and locator information has been captured (including any restrictions on how the subject may be contacted, if at all). The consent and locator mixins are available in projects `edc_consent` and `edc_locator`. Personal information is always encrypted at rest in any EDC model (see modules `django_crypto_fields` and `edc.core.crypto_fields`).


## Expected Flow

* ICF, complete `Consent` Form
* Complete `Locator` Form
* Complete the `ModelCaller` scheduling form (in the example this is `AntenatalEnrollment`)
* Go to Call in Admin
* Tick a participant to call
* Select `Call Participant` action item and click Go
* Complete the Log Entry for this call attempt

## Making a call and updating the `Log`

Calls are made via the Call changelist in Admin. A researcher pulls up the Log by ticking the call instance for the participant, selecting the `Call Participant` action item, and clikcing Go. The EDC will navigate to the Add/Change view of the Log and Log Entries.




