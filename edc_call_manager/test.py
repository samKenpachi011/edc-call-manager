from datetime import datetime

from django.db import models
from django.test import TestCase
from django.db.models.signals import post_save
from django.dispatch import receiver

from edc_call_manager.site import site, AlreadyRegistered
from edc_call_manager.model_caller import ModelCaller, WEEKLY
from edc_call_manager.decorators import register
from edc_call_manager.models import Call
from edc_constants.constants import CLOSED, NEW


@receiver(post_save, weak=False, dispatch_uid='model_caller_on_post_save')
def model_caller_on_post_save(sender, instance, raw, created, using, update_fields, **kwargs):
    if not raw and created:
        site.schedule_calls(sender, instance)
        site.unschedule_calls(sender, instance)


class TestModel(models.Model):

    subject_identifier = models.CharField(
        max_length=25)

    subject_date = models.DateField(
        default=datetime.now())

    class Meta:
        app_label = 'edc_call_manager'


class TestStartModel(models.Model):

    subject_identifier = models.CharField(
        max_length=25)

    subject_date = models.DateField(
        default=datetime.now())

    class Meta:
        app_label = 'edc_call_manager'


class TestStopModel(models.Model):

    subject_identifier = models.CharField(
        max_length=25)

    subject_date = models.DateField(
        default=datetime.now())

    class Meta:
        app_label = 'edc_call_manager'


@register(TestModel)
class TestModelCaller(ModelCaller):
    pass


@register(TestStartModel)
class RepeatingTestModelCaller(ModelCaller):
    label = 'My test caller'
    unscheduling_model = TestStopModel
    interval = WEEKLY


class TestCaller(TestCase):

    def test_register(self):
        self.assertIn(TestModel, site.scheduling_models)

    def test_register_duplicate(self):
        class TestModelCaller2(ModelCaller):
            pass
        self.assertRaises(AlreadyRegistered, site.register, TestModel, TestModelCaller2)

    def test_create_registered_model(self):
        TestModel.objects.create(subject_identifier='1111111')
        self.assertEqual(Call.objects.filter(subject_identifier='1111111').count(), 1)

    def test_call_defaults(self):
        TestModel.objects.create(subject_identifier='1111111')
        call = Call.objects.get(subject_identifier='1111111')
        self.assertEqual(call.label, 'testmodelcaller')
        self.assertFalse(call.repeats)

    def test_repeating_caller_defaults(self):
        TestStartModel.objects.create(subject_identifier='1111111')
        call = Call.objects.get(subject_identifier='1111111')
        self.assertEqual(call.label, 'my-test-caller')
        self.assertTrue(call.repeats)

    def test_unscheduling_ignores_if_no_scheduled(self):
        TestStopModel.objects.create(subject_identifier='1111111')
        self.assertRaises(Call.DoesNotExist, Call.objects.get, subject_identifier='1111111')

    def test_unscheduling_closes_if_scheduled(self):
        TestStartModel.objects.create(subject_identifier='1111111')
        self.assertEqual(Call.objects.filter(
            subject_identifier='1111111',
            call_status=NEW).count(), 1)
        TestStopModel.objects.create(subject_identifier='1111111')
        self.assertEqual(Call.objects.filter(
            subject_identifier='1111111',
            call_status=CLOSED).count(), 1)
