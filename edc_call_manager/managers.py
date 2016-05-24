from django.db import models


class CallManager(models.Manager):
    def get_by_natural_key(self, subject_identifier, label, scheduled):
        return self.get(subject_identifier=subject_identifier, label=label, scheduled=scheduled)


class LogManager(models.Manager):
    def get_by_natural_key(self, log_datetime, subject_identifier, label, scheduled):
        return self.get(
            log_datetime=log_datetime,
            subject_identifier=subject_identifier, label=label, scheduled=scheduled)


class LogEntryManager(models.Manager):
    def get_by_natural_key(self, call_datetime, log_datetime, subject_identifier, label, scheduled):
        return self.get(
            call_datetime=call_datetime,
            log_datetime=log_datetime,
            subject_identifier=subject_identifier, label=label, scheduled=scheduled)
