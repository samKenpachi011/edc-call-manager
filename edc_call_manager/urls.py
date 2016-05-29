from django.conf.urls import url

from edc_call_manager.views import CallSubjectUpdateView, CallSubjectDeleteView, CallSubjectCreateView

from .admin import call_manager_admin


urlpatterns = [
    url(r'^callsubject/(?P<caller_app>\w+)/(?P<caller_model>\w+)/(?P<log_pk>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/add/$',
        CallSubjectCreateView.as_view(), name='call-subject-add'),
    url(r'^callsubject/(?P<caller_app>\w+)/(?P<caller_model>\w+)/(?P<log_pk>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/(?P<pk>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/',
        CallSubjectUpdateView.as_view(), name='call-subject-update'),
    url(r'^callsubject/(?P<caller_app>\w+)/(?P<caller_model>\w+)/(?P<pk>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/delete/$',
        CallSubjectDeleteView.as_view(), name='call-subject-delete'),
    url(r'^admin/', call_manager_admin.urls)
]
