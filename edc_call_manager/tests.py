import json

from datetime import date, timedelta

from django.apps import apps as django_apps
from django.core import serializers
from django.test.testcases import TestCase

from edc_base.utils import get_utcnow
from edc_constants.constants import CLOSED, YES, NO, ALIVE, DEAD
from edc_registration.models import RegisteredSubject
from example.models import TestModel, TestStartModel, TestStopModel, TestStopTwoModel, Locator

from .caller_site import site_model_callers, AlreadyRegistered
from .constants import OPEN_CALL, NEW_CALL
from .model_caller import ModelCaller, WEEKLY

app_config = django_apps.get_app_config('edc_call_manager')
Call = django_apps.get_model(app_config.app_label, 'call')
Log = django_apps.get_model(app_config.app_label, 'log')
LogEntry = django_apps.get_model(app_config.app_label, 'logentry')


class TestModelCaller(ModelCaller):
    label = 'TestModelCaller'
    app_label = 'edc_call_manager_example'
    locator_model = Locator
    subject_model = RegisteredSubject


class RepeatingTestModelCaller(ModelCaller):
    label = 'RepeatingTestModelCaller'
    app_label = 'edc_call_manager_example'
    locator_model = Locator
    subject_model = RegisteredSubject
    interval = WEEKLY


class LocatorTestModelCaller(ModelCaller):
    label = 'LocatorTestModelCaller'
    app_label = 'edc_call_manager_example'
    interval = WEEKLY
    locator_model = Locator
    subject_model = RegisteredSubject


class TestCallManager(TestCase):

    def setUp(self):
        site_model_callers.reset_registry()
        site_model_callers.register(TestModelCaller, TestModel, TestStopModel, verbose=False)
        site_model_callers.register(RepeatingTestModelCaller, TestStartModel, TestStopTwoModel, verbose=False)
        self.subject_identifier = '1111111'
        self.registered_subject = RegisteredSubject.objects.create(subject_identifier='1111111')

    def test_model_factory(self):
        return TestModel.objects.create(
            subject_identifier=self.subject_identifier)
 
    def test_start_model_factory(self):
        return TestStartModel.objects.create(
            subject_identifier=self.subject_identifier)
#   
    def test_stop_model_factory(self):
        return TestStopModel.objects.create(
            subject_identifier=self.subject_identifier)

    def test_stop_two_model_factory(self):
        return TestStopTwoModel.objects.create(
            subject_identifier=self.subject_identifier)
#  
    def test_register(self):
        """Test if start models are registered.
        """
        self.assertIn(TestModel, site_model_callers.start_models)
        self.assertIn(TestStartModel, site_model_callers.start_models)
  
    def test_register_duplicate(self):
        """Test if re-registering and already registered model throws an error.
        """
        class TestModelCaller2(ModelCaller):
            pass
        self.assertRaises(AlreadyRegistered, site_model_callers.register, TestModelCaller2, TestModel, TestStopModel)
 
    def test_create_registered_model(self):
        """Testt iff a start model created a call instance.
        """
        TestModel.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertEqual(Call.objects.filter(subject_identifier=self.subject_identifier).count(), 1)
#  
    def test_call_defaults(self):
        """Test that repeats set to default for a call.
        """
        self.test_model_factory()
        call = Call.objects.get(subject_identifier=self.subject_identifier)
        self.assertEqual(call.label, 'testmodelcaller')
        self.assertFalse(call.repeats)
  
    def test_repeating_caller_defaults(self):
        """Test that repeat is set to True for a call that repeats.
        """
        self.test_start_model_factory()
        call = Call.objects.get(subject_identifier=self.subject_identifier)
        self.assertEqual(call.label, 'RepeatingTestModelCaller'.lower())
        self.assertTrue(call.repeats)
  
    def test_unscheduling_ignores_if_no_scheduled(self):
        """Test if an unschedule model does nothing if a call was never scheduled.
        """
        self.test_stop_model_factory()
        self.assertRaises(Call.DoesNotExist, Call.objects.get, subject_identifier=self.subject_identifier)
  
    def test_unscheduling_closes_if_scheduled(self):
        """Test that for a scheduled call, a stop model is able to close a call when created.
        """
        self.assertEqual(
            Call.objects.filter(
                subject_identifier=self.subject_identifier,
                label='RepeatingTestModelCaller'.lower(),
                call_status=NEW_CALL).count(), 0)
        self.assertEqual(
            Call.objects.filter(
                subject_identifier=self.subject_identifier,
                label='RepeatingTestModelCaller'.lower(),
                call_status=CLOSED).count(), 0)
        self.test_start_model_factory()
        self.assertEqual(
            Call.objects.filter(
                subject_identifier=self.subject_identifier,
                label='RepeatingTestModelCaller'.lower(),
                call_status=NEW_CALL).count(), 1)
        self.test_stop_two_model_factory()
        self.assertEqual(
            Call.objects.filter(
                subject_identifier=self.subject_identifier,
                label='RepeatingTestModelCaller'.lower(),
                call_status=CLOSED).count(), 1)
  
    def test_locator_not_found_for_log(self):
        """Test that an missing locator iformation is set if does not exist for a log.
        """
        site_model_callers.reset_registry()
        site_model_callers.register(LocatorTestModelCaller, TestStartModel, verbose=False)
        self.test_start_model_factory()
        call = Call.objects.get(
            subject_identifier=self.subject_identifier,
            call_status=NEW_CALL)
        log = Log.objects.get(call=call)
        self.assertEqual(log.locator_information, 'locator not found.')
  
    def test_locator_as_string_for_log(self):
        """Test that locator information is stttored as a string in a the log.
        """
        site_model_callers.reset_registry()
        site_model_callers.register(LocatorTestModelCaller, TestStartModel, verbose=False)
        Locator.objects.create(
            subject_identifier=self.subject_identifier,
            may_visit_home=YES,
            physical_address='Near General Dealer with black steel gate',
            subject_cell='723333333',
            may_call_work=NO,
            may_contact_indirectly=NO)
        self.test_start_model_factory()
        call = Call.objects.get(
            subject_identifier=self.subject_identifier,
            call_status=NEW_CALL)
        log = Log.objects.get(call=call)
        self.assertIn('723333333', log.locator_information)
  
    def test_log_entry_outcome_call_again(self):
        """Test that a log entry update the call outcome for an alive participant.
        """
        self.test_start_model_factory()
        call = Call.objects.get(
            subject_identifier=self.subject_identifier,
            call_status=NEW_CALL)
        call_pk = call.pk
        log = Log.objects.get(call=call)
        LogEntry.objects.create(
            log=log,
            call_datetime=get_utcnow(),
            contact_type='direct',
            survival_status=ALIVE)
        call = Call.objects.get(pk=call_pk)
        self.assertIn('Alive', call.call_outcome)
  
    def test_log_entry_outcome_deceased(self):
        """Test that a log entry update the call outcome for a deceased participant.
        """
        self.test_start_model_factory()
        call = Call.objects.get(
            subject_identifier=self.subject_identifier,
            call_status=NEW_CALL)
        call_pk = call.pk
        log = Log.objects.get(call=call)
        LogEntry.objects.create(
            log=log,
            call_datetime=get_utcnow(),
            contact_type='indirect',
            survival_status=DEAD)
        call = Call.objects.get(pk=call_pk)
        self.assertEqual(call.call_status, CLOSED)
        self.assertIn('Deceased', call.call_outcome)
  
    def test_call_attempts(self):
        """Test that attempts made for calls is updated after every call.
        """
        subject_identifier = self.subject_identifier
        self.test_start_model_factory()
        call = Call.objects.get(
            subject_identifier=subject_identifier,
            call_status=NEW_CALL)
        call_pk = call.pk
        log = Log.objects.get(call=call)
        LogEntry.objects.create(
            log=log,
            call_datetime=get_utcnow(),
            contact_type='indirect',
            survival_status=ALIVE)
        call = Call.objects.get(pk=call_pk)
        self.assertEqual(call.call_attempts, 1)
        self.assertEqual(call.call_status, OPEN_CALL)
        LogEntry.objects.create(
            log=log,
            call_datetime=get_utcnow(),
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
        """Test if a next call is schedule once another is closed.
        """
        subject_identifier = self.subject_identifier
        self.test_start_model_factory()
        call = Call.objects.get(
            subject_identifier=subject_identifier,
            call_status=NEW_CALL)
        call_pk = call.pk
        call_label = call.label
        log = Log.objects.get(call=call)
        LogEntry.objects.create(
            log=log,
            call_datetime=get_utcnow(),
            contact_type='indirect',
            survival_status=ALIVE,
            appt=YES,
            appt_date=date.today() + timedelta(days=5))
        call = Call.objects.get(pk=call_pk)
        self.assertEqual(call.call_status, CLOSED)
        self.assertEqual(Call.objects.filter(
            subject_identifier=subject_identifier,
            label=call_label,
            call_status=NEW_CALL).exclude(pk=call_pk).count(), 1)
        scheduled = Call.objects.filter(
            subject_identifier=subject_identifier,
            label=call_label,
            call_status=NEW_CALL).exclude(pk=call_pk)[0].scheduled
        self.assertGreater(scheduled, call.scheduled)
  
    def test_call_serialize(self):
        """Test if the call object is serializeble.
        """
        self.test_model_factory()
        call = Call.objects.get(subject_identifier=self.subject_identifier)
        json_object = serializers.serialize(
            'json', [call], use_natural_foreign_keys=True, use_natural_primary_keys=True)
        self.assertTrue(json.loads(json_object))
  
    def test_log_serialize(self):
        """Test if the call log object is serializeble.
        """
        self.test_model_factory()
        call = Call.objects.get(subject_identifier=self.subject_identifier)
        log = Log.objects.get(call=call)
        json_object = serializers.serialize(
            'json', [log], use_natural_foreign_keys=True, use_natural_primary_keys=True)
        self.assertTrue(json.loads(json_object))
        obj = json.loads(json_object)
        self.assertEqual(
            obj[0]['fields']['call'],
            [self.subject_identifier, TestModelCaller.label.lower(), date.today().strftime('%Y-%m-%d')])
  
    def test_logentry_serialize(self):
        """Test if the call log entry object is serializeble.
        """
        self.test_model_factory()
        call = Call.objects.get(subject_identifier=self.subject_identifier)
        log = Log.objects.get(call=call)
        now = get_utcnow()
        today = date.today()
        log_entry = LogEntry.objects.create(
            log=log,
            call_datetime=now,
            contact_type='indirect',
            survival_status=ALIVE,
            appt=YES,
            appt_date=today + timedelta(days=5))
        json_object = serializers.serialize(
            'json', [log_entry], use_natural_foreign_keys=True, use_natural_primary_keys=True)
        self.assertTrue(json.loads(json_object))
        obj = json.loads(json_object)
        self.assertEqual(
            obj[0]['fields']['log'][0][:-5], now.isoformat()[:-13])
        self.assertEqual(
            obj[0]['fields']['log'][1:],
            [self.subject_identifier, TestModelCaller.label.lower(), date.today().strftime('%Y-%m-%d')])
