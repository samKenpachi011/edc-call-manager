from datetime import date

from django.db import models
from django.utils import timezone

from edc_locator.mixins import LocatorMixin


class Locator(LocatorMixin, models.Model):

    subject_identifier = models.CharField(
        max_length=25)

    class Meta:
        app_label = 'example'


class Consent(models.Model):

    subject_identifier = models.CharField(
        max_length=25)

    consent_datetime = models.DateTimeField(default=timezone.now)

    first_name = models.CharField(max_length=25)

    initials = models.CharField(max_length=3)

    class Meta:
        app_label = 'example'


class TestStartModel(models.Model):

    subject_identifier = models.CharField(
        max_length=25)

    report_datetime = models.DateField(
        default=date.today)

    class Meta:
        app_label = 'example'


class TestStopModel(models.Model):

    subject_identifier = models.CharField(
        max_length=25)

    report_datetime = models.DateField(
        default=date.today)

    class Meta:
        app_label = 'example'
