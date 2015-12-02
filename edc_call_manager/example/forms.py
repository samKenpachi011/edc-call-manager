from django import forms

from edc_call_manager.example.models import TestStartModel, TestStopModel, Consent


class TestStartModelForm(forms.ModelForm):

    class Meta:
        model = TestStartModel
        fields = '__all__'


class TestStopModelForm(forms.ModelForm):

    class Meta:
        model = TestStopModel
        fields = '__all__'


class ConsentForm(forms.ModelForm):

    class Meta:
        model = Consent
        fields = '__all__'
