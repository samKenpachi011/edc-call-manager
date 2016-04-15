from django.test import TestCase

from edc_base.utils import edc_base_startup


class BaseTestCase(TestCase):

    def setUp(self):
        edc_base_startup()
