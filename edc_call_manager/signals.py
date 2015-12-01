from django.db.models.signals import post_save

from django.dispatch import receiver

from edc_call_manager.site import site


@receiver(post_save, weak=False, dispatch_uid='model_caller_on_post_save')
def model_caller_on_post_save(sender, instance, raw, created, using, update_fields, **kwargs):
    if not raw and created:
        site.schedule_calls(sender, instance)
        site.unschedule_calls(sender, instance)
