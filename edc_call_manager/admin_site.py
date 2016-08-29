from django.contrib.admin import AdminSite


class EdcCallManagerAdminSite(AdminSite):
    site_header = 'Call Manager'
    site_title = 'Call Manager'
    index_title = 'Call Manager Administration'
    site_url = '/call_manager/'
edc_call_manager_admin = EdcCallManagerAdminSite(name='edc_call_manager_admin')
