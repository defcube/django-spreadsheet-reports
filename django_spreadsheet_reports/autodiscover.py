import importlib.util
from django.apps.config import AppConfig
from django.conf import settings

def autodiscover():
    # Check django/contrib/admin/__init__.py to know what I'm doing :)
    for app in settings.INSTALLED_APPS:
        reports_spec = app + ".reports"
        if importlib.util.find_spec(reports_spec) is None:
            continue

        __import__(reports_spec)


class MyAppConfig(AppConfig):
    name = 'django_spreadsheet_reports'

    def ready(self):
        autodiscover()

