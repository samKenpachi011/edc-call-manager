from django.urls.conf import re_path
from django.views.generic.base import RedirectView

from django.urls.conf import path

from edc_constants.constants import UUID_PATTERN

from .views import HomeView, CallSubjectUpdateView, CallSubjectDeleteView, CallSubjectCreateView
from .admin_site import edc_call_manager_admin

app_name = 'edc_call_manager'

urlpatterns = [
    path(r'admin/', edc_call_manager_admin.urls),
    path(r'', HomeView.as_view(), name='home_url'),

    re_path(r'^' + f'{app_name}/(?P<caller_label>\\w+)/'
            f'(?P<log_pk>{UUID_PATTERN.pattern})//add/',
            CallSubjectCreateView.as_view(), name='call-subject-add'),
]
