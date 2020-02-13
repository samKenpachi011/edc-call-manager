from django.urls.conf import path

from .views import HomeView, CallSubjectUpdateView, CallSubjectDeleteView, CallSubjectCreateView
from .admin_site import edc_call_manager_admin

app_name = 'edc_call_manager'

urlpatterns = [
    path('admin/', edc_call_manager_admin.urls),
    path(r'^(?P<caller_label>\w+)/(?P<log_pk>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/add/$',
        CallSubjectCreateView.as_view(), name='call-subject-add'),
    path(r'^callsubject/(?P<caller_label>\w+)/(?P<log_pk>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/'
        '(?P<pk>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/change/',
        CallSubjectUpdateView.as_view(), name='call-subject-change'),
    path(r'^callsubject/(?P<caller_app_label>\w+)/(?P<caller_model_name>\w+)/'
        '(?P<pk>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/delete/$',
        CallSubjectDeleteView.as_view(), name='call-subject-delete'),
    path(r'', HomeView.as_view(), name='home_url')
]
