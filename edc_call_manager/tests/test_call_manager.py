from datetime import date, timedelta
from django.utils import timezone

from edc_call_manager.caller_site import site_model_callers, AlreadyRegistered
from edc_call_manager.model_caller import ModelCaller, WEEKLY
from edc_constants.constants import CLOSED, NEW, YES, NO, ALIVE, DEAD, OPEN

from example.models import (
    TestModel, TestStartModel, TestStopModel, Locator, Call, Log, LogEntry, RegisteredSubject)

from django.test.testcases import TestCase


class TestModelCaller(ModelCaller):
    label = 'TestModelCaller'
    call_model = Call
    log_entry_model = LogEntry
    log_model = Log
    locator_model = Locator
    unscheduling_model = TestStopModel


class RepeatingTestModelCaller(ModelCaller):
    label = 'RepeatingTestModelCaller'
    call_model = Call
    log_entry_model = LogEntry
    log_model = Log
    locator_model = Locator
    unscheduling_model = TestStopModel
    interval = WEEKLY


class LocatorTestModelCaller(ModelCaller):
    label = 'LocatorTestModelCaller'
    call_model = Call
    log_entry_model = LogEntry
    log_model = Log
    unscheduling_model = TestStopModel
    interval = WEEKLY
    locator_model = Locator


class TestCallManager(TestCase):

    def test_model_factory(self):
        return TestModel.objects.create(
            registered_subject=self.registered_subject,
            subject_identifier=self.subject_identifier)

    def test_start_model_factory(self):
        return TestStartModel.objects.create(
            registered_subject=self.registered_subject,
            subject_identifier=self.subject_identifier)

    def test_stop_model_factory(self):
        return TestStopModel.objects.create(
            registered_subject=self.registered_subject,
            subject_identifier=self.subject_identifier)

    def setUp(self):

        site_model_callers.reset_registry()
        site_model_callers.register(TestModel, TestModelCaller, verbose=False)
        site_model_callers.register(TestStartModel, RepeatingTestModelCaller, verbose=False)
        self.subject_identifier = '1111111'
        self.registered_subject = RegisteredSubject.objects.create(
            subject_identifier='1111111', subject_type='subject')

    def test_register(self):
        self.assertIn(TestModel, site_model_callers.scheduling_models)
        self.assertIn(TestStartModel, site_model_callers.scheduling_models)

    def test_register_duplicate(self):
        class TestModelCaller2(ModelCaller):
            pass
        self.assertRaises(AlreadyRegistered, site_model_callers.register, TestModel, TestModelCaller2)

    def test_create_registered_model(self):
        TestModel.objects.create(
            registered_subject=self.registered_subject,
            subject_identifier=self.subject_identifier)
        self.assertEqual(Call.objects.filter(subject_identifier=self.subject_identifier).count(), 1)

    def test_call_defaults(self):
        self.test_model_factory()
        call = Call.objects.get(subject_identifier=self.subject_identifier)
        self.assertEqual(call.label, 'testmodelcaller')
        self.assertFalse(call.repeats)

    def test_repeating_caller_defaults(self):
        self.test_start_model_factory()
        call = Call.objects.get(subject_identifier=self.subject_identifier)
        self.assertEqual(call.label, 'RepeatingTestModelCaller'.lower())
        self.assertTrue(call.repeats)

#     def test_scheduling_registeredsubject_reference_model(self):
#         TestRegisteredSubjectReferenceModel.objects.create(
#             subject_identifier=self.registered_subject.subject_identifier,
#             registered_subject=self.registered_subject)
#         self.assertEqual(Call.objects.filter(
#             registered_subject__subject_identifier=self.subject_identifier).count(), 1)

    def test_unscheduling_ignores_if_no_scheduled(self):
        self.test_stop_model_factory()
        self.assertRaises(Call.DoesNotExist, Call.objects.get, subject_identifier=self.subject_identifier)

    def test_unscheduling_closes_if_scheduled(self):
        registered_subject = self.test_start_model_factory().registered_subject
        self.assertEqual(
            Call.objects.filter(
                registered_subject=registered_subject,
                subject_identifier=self.subject_identifier,
                label='RepeatingTestModelCaller'.lower(),
                call_status=NEW).count(), 1)
        self.test_stop_model_factory()
        self.assertEqual(
            Call.objects.filter(
                registered_subject=registered_subject,
                subject_identifier=self.subject_identifier,
                label='RepeatingTestModelCaller'.lower(),
                call_status=CLOSED).count(), 1)

    def test_locator_not_found_for_log(self):
        site_model_callers.reset_registry()
        site_model_callers.register(TestStartModel, LocatorTestModelCaller, verbose=False)
        self.test_start_model_factory()
        call = Call.objects.get(
            subject_identifier=self.subject_identifier,
            call_status=NEW)
        log = Log.objects.get(call=call)
        self.assertEqual(log.locator_information, 'locator not found.')

    def test_locator_as_string_for_log(self):
        site_model_callers.reset_registry()
        site_model_callers.register(TestStartModel, LocatorTestModelCaller, verbose=False)
        locator = Locator.objects.create(
            subject_identifier=self.subject_identifier,
            home_visit_permission=YES,
            physical_address='Near General Dealer with black steel gate',
            may_follow_up=YES,
            subject_cell='723333333',
            may_call_work=NO,
            may_contact_someone=NO)
        self.test_start_model_factory()
        call = Call.objects.get(
            subject_identifier=self.subject_identifier,
            call_status=NEW)
        log = Log.objects.get(call=call)
        self.assertEqual(log.locator_information, locator.to_string())
        self.assertIn('723333333', log.locator_information)

    def test_log_entry_outcome_call_again(self):
        self.test_start_model_factory()
        call = Call.objects.get(
            subject_identifier=self.subject_identifier,
            call_status=NEW)
        call_pk = call.pk
        log = Log.objects.get(call=call)
        LogEntry.objects.create(
            log=log,
            call_datetime=timezone.now(),
            contact_type='direct',
            survival_status=ALIVE)
        call = Call.objects.get(pk=call_pk)
        self.assertIn('Alive', call.call_outcome)

    def test_log_entry_outcome_deceased(self):
        self.test_start_model_factory()
        call = Call.objects.get(
            subject_identifier=self.subject_identifier,
            call_status=NEW)
        call_pk = call.pk
        log = Log.objects.get(call=call)
        LogEntry.objects.create(
            log=log,
            call_datetime=timezone.now(),
            contact_type='indirect',
            survival_status=DEAD)
        call = Call.objects.get(pk=call_pk)
        self.assertEqual(call.call_status, CLOSED)
        self.assertIn('Deceased', call.call_outcome)

    def test_call_attempts(self):
        subject_identifier = self.subject_identifier
        self.test_start_model_factory()
        call = Call.objects.get(
            subject_identifier=subject_identifier,
            call_status=NEW)
        call_pk = call.pk
        log = Log.objects.get(call=call)
        LogEntry.objects.create(
            log=log,
            call_datetime=timezone.now(),
            contact_type='indirect',
            survival_status=ALIVE)
        call = Call.objects.get(pk=call_pk)
        self.assertEqual(call.call_attempts, 1)
        self.assertEqual(call.call_status, OPEN)
        LogEntry.objects.create(
            log=log,
            call_datetime=timezone.now(),
            contact_type='direct',
            survival_status=ALIVE,
            appt=YES,
            appt_date=date.today() + timedelta(5))
        call = Call.objects.get(pk=call_pk)
        self.assertEqual(call.call_attempts, 2)
        self.assertEqual(call.call_status, CLOSED)
        # created a new call after closing the previous
        self.assertEqual(Call.objects.filter(
            subject_identifier=subject_identifier, label=call.label).count(), 2)

    def test_schedule_next_call(self):
        subject_identifier = self.subject_identifier
        self.test_start_model_factory()
        call = Call.objects.get(
            subject_identifier=subject_identifier,
            call_status=NEW)
        call_pk = call.pk
        call_label = call.label
        log = Log.objects.get(call=call)
        LogEntry.objects.create(
            log=log,
            call_datetime=timezone.now(),
            contact_type='indirect',
            survival_status=ALIVE,
            appt=YES,
            appt_date=date.today() + timedelta(days=5))
        call = Call.objects.get(pk=call_pk)
        self.assertEqual(call.call_status, CLOSED)
        self.assertEqual(Call.objects.filter(
            subject_identifier=subject_identifier,
            label=call_label,
            call_status=NEW).exclude(pk=call_pk).count(), 1)
        scheduled = Call.objects.filter(
            subject_identifier=subject_identifier,
            label=call_label,
            call_status=NEW).exclude(pk=call_pk)[0].scheduled
        self.assertGreater(scheduled, call.scheduled)
