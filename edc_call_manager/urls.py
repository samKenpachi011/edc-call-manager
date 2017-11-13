from django.contrib import admin
from django.conf.urls import url

from .views import HomeView, CallSubjectUpdateView, CallSubjectDeleteView, CallSubjectCreateView


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^(?P<caller_label>\w+)/(?P<log_pk>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/add/$',
        CallSubjectCreateView.as_view(), name='call-subject-add'),
    url(r'^callsubject/(?P<caller_label>\w+)/(?P<log_pk>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/'
        '(?P<pk>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/change/',
        CallSubjectUpdateView.as_view(), name='call-subject-change'),
    url(r'^callsubject/(?P<caller_app_label>\w+)/(?P<caller_model_name>\w+)/'
        '(?P<pk>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/delete/$',
        CallSubjectDeleteView.as_view(), name='call-subject-delete'),
    url(r'', HomeView.as_view(), name='home')
]
