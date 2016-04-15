from django.contrib import admin

from .forms import TestStartModelForm, TestStopModelForm, ConsentForm
from .models import TestStartModel, TestStopModel, Consent, Locator


class TestStartModelAdmin(admin.ModelAdmin):
    form = TestStartModelForm
admin.site.register(TestStartModel, TestStartModelAdmin)


class TestStopModelAdmin(admin.ModelAdmin):
    form = TestStopModelForm
admin.site.register(TestStopModel, TestStopModelAdmin)


class ConsentAdmin(admin.ModelAdmin):
    form = ConsentForm
admin.site.register(Consent, ConsentAdmin)


class LocatorAdmin(admin.ModelAdmin):
    pass
admin.site.register(Locator, LocatorAdmin)
