from django.urls.conf import path, include
from django.contrib import admin
from django.views.generic.base import RedirectView

from edc_base.views import LoginView, LogoutView
from edc_call_manager.admin import edc_call_manager_admin

from .views import HomeView

urlpatterns = [
    path('login', LoginView.as_view(), name='login_url'),
    path('logout', LogoutView.as_view(pattern_name='login_url'), name='logout_url'),
    # url(r'^call_manager/$', RedirectView.as_view(pattern_name='home_url')),
    path('call_manager/', include('edc_call_manager.urls', namespace='edc-call-manager')),
    path('edc/', include('edc_base.urls')),
    path('admin/', RedirectView.as_view(pattern_name='home_url')),
    path('admin/', edc_call_manager_admin.urls),
    path('admin/', admin.site.urls),
    path('home/', HomeView.as_view(), name='home_url'),
    path('', HomeView.as_view(), name='home_url'),
]


admin.site.site_header = 'Example'
admin.site.site_title = 'Example'
admin.site.index_title = 'Example Admin'
admin.site.site_url = '/'
