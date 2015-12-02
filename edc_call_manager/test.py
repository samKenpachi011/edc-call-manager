from django.db import models
from django.test import TestCase

from edc_call_manager.caller_site import site_model_callers, AlreadyRegistered
from edc_call_manager.model_caller import ModelCaller, WEEKLY
from edc_call_manager.models import Call, Log, LogEntry
from edc_constants.constants import CLOSED, NEW, YES, NO, ALIVE, DEAD
from edc_locator.mixins import LocatorMixin
from django.utils import timezone


class TestModel(models.Model):

    subject_identifier = models.CharField(
        max_length=25)

    report_datetime = models.DateField(
        default=timezone.now())

    class Meta:
        app_label = 'edc_call_manager'


class Locator(LocatorMixin, models.Model):

    subject_identifier = models.CharField(
        max_length=25)

    class Meta:
        app_label = 'edc_call_manager'


class TestStartModel(models.Model):

    subject_identifier = models.CharField(
        max_length=25)

    report_datetime = models.DateField(
        default=timezone.now())

    class Meta:
        app_label = 'edc_call_manager'


class TestStopModel(models.Model):

    subject_identifier = models.CharField(
        max_length=25)

    report_datetime = models.DateField(
        default=timezone.now())

    class Meta:
        app_label = 'edc_call_manager'


class TestModelCaller(ModelCaller):
    pass


class RepeatingTestModelCaller(ModelCaller):
    label = 'My test caller'
    unscheduling_model = TestStopModel
    interval = WEEKLY


class LocatorTestModelCaller(ModelCaller):
    label = 'My test caller'
    unscheduling_model = TestStopModel
    interval = WEEKLY
    locator_model = Locator


class TestCaller(TestCase):

    def setUp(self):

        site_model_callers.reset_registry()
        site_model_callers.register(TestModel, TestModelCaller)
        site_model_callers.register(TestStartModel, RepeatingTestModelCaller)

    def test_register(self):
        self.assertIn(TestModel, site_model_callers.scheduling_models)

    def test_register_duplicate(self):
        class TestModelCaller2(ModelCaller):
            pass
        self.assertRaises(AlreadyRegistered, site_model_callers.register, TestModel, TestModelCaller2)

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

    def test_locator_not_found_for_log(self):
        site_model_callers.reset_registry()
        site_model_callers.register(TestStartModel, LocatorTestModelCaller)
        TestStartModel.objects.create(subject_identifier='1111111')
        call = Call.objects.get(
            subject_identifier='1111111',
            call_status=NEW)
        log = Log.objects.get(call=call)
        self.assertEqual(log.locator_information, 'locator not found.')

    def test_locator_as_string_for_log(self):
        site_model_callers.reset_registry()
        site_model_callers.register(TestStartModel, LocatorTestModelCaller)
        locator = Locator.objects.create(
            subject_identifier='1111111',
            home_visit_permission=YES,
            physical_address='Near General Dealer with black steel gate',
            may_follow_up=YES,
            subject_cell='723333333',
            may_call_work=NO,
            may_contact_someone=NO)
        TestStartModel.objects.create(subject_identifier='1111111')
        call = Call.objects.get(
            subject_identifier='1111111',
            call_status=NEW)
        log = Log.objects.get(call=call)
        self.assertEqual(log.locator_information, locator.to_string())
        self.assertIn('723333333', log.locator_information)

    def test_log_entry_outcome_call_again(self):
        TestStartModel.objects.create(subject_identifier='1111111')
        call = Call.objects.get(
            subject_identifier='1111111',
            call_status=NEW)
        call_pk = call.pk
        log = Log.objects.get(call=call)
        LogEntry.objects.create(
            log=log,
            call_datetime=timezone.now(),
            contact_type='direct',
            survival_status=ALIVE)
        call = Call.objects.get(pk=call_pk)
        self.assertIn('Alive. Call again', call.call_outcome)

    def test_log_entry_outcome_deceased(self):
        TestStartModel.objects.create(subject_identifier='1111111')
        call = Call.objects.get(
            subject_identifier='1111111',
            call_status=NEW)
        call_pk = call.pk
        log = Log.objects.get(call=call)
        log_entry = LogEntry.objects.create(
            log=log,
            call_datetime=timezone.now(),
            contact_type='indirect',
            survival_status=DEAD)
        self.assertEqual(log_entry.call_again, NO)
        call = Call.objects.get(pk=call_pk)
        self.assertEqual(call.call_status, CLOSED)
        self.assertIn('Alive. Do not call', call.call_outcome)

    def test_call_attempts(self):
        TestStartModel.objects.create(subject_identifier='1111111')
        call = Call.objects.get(
            subject_identifier='1111111',
            call_status=NEW)
        call_pk = call.pk
        log = Log.objects.get(call=call)
        LogEntry.objects.create(
            log=log,
            call_datetime=timezone.now(),
            contact_type='indirect',
            survival_status=ALIVE,
            call_again=YES)
        LogEntry.objects.create(
            log=log,
            call_datetime=timezone.now(),
            contact_type='direct',
            survival_status=ALIVE,
            call_again=NO)
        call = Call.objects.get(pk=call_pk)
        self.assertEqual(call.call_attempts, 2)
