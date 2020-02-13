from django.contrib.admin import AdminSite


class AdminSite(AdminSite):
    site_header = 'EDC Call Manager'
    site_title = 'EDC Call Manager'
    index_title = 'Call Manager Administration'
    site_url = '/administration/'

edc_call_manager_admin = AdminSite(name='edc_call_manager_admin')
