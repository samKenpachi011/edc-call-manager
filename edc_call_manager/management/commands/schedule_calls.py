from django.core.management.base import BaseCommand, CommandError
from django.apps import apps as django_apps

from edc_call_manager.caller_site import site_model_callers
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist


class Command(BaseCommand):

    help = 'Schedule calls for given model caller if not already scheduled'

    def add_arguments(self, parser):
        parser.add_argument(
            'model_caller', type=str, help='Model caller app_label.model_name')

    def handle(self, *args, **options):
        try:
            model = django_apps.get_model(*options['model_caller'].split('.'))
        except LookupError:
            raise CommandError(
                'Unknown app_label.model_name. Got \'{}\''.format(options['model_caller']))
        try:
            model_caller = site_model_callers.get_model_caller(model)
        except KeyError:
            raise CommandError('Unknown model caller for app_label.model_name. Got \'{}\''.format(
                options['model_caller']))
        self.stdout.write(
            self.style.SUCCESS('Found model_caller \'{}\' with call model \'{}\'.'.format(
                model_caller.label, model_caller.call_model)))
        new_calls = 0
        for obj in model.objects.all():
            try:
                model_caller.call_model.objects.get(
                    subject_identifier=obj.subject_identifier, label=model_caller.label)
            except MultipleObjectsReturned:
                pass
            except ObjectDoesNotExist:
                site_model_callers.schedule_calls(model, obj)
                new_calls += 1
        if new_calls > 0:
            self.stdout.write(
                self.style.SUCCESS('Successfully scheduled calls for {} {}'.format(
                    new_calls, model._meta.verbose_name)))
        else:
            self.stdout.write(
                self.style.SUCCESS('No new calls scheduled. At least one call for each {} is already scheduled.'.format(
                    new_calls, model._meta.verbose_name)))
