from django.conf import settings
from .reports import Report, Column, columns, filters, Filter, groupbys, GroupBy, DateFilter, \
    CalculatedColumn, PercentageCalculatedColumn, BooleanFilter, DecimalColumn, HiddenColumn, \
    ChoicesColumn, PercentageDifferenceColumn
from .reporting_site import site


REPORTING_SOURCE_FILE = 'reports'


# def autodiscover():
#     # Check django/contrib/admin/__init__.py to know what I'm doing :)
#     for app in settings.INSTALLED_APPS:
#         try:
#             app_path = __import__(app, {}, {}, [app.split('.')[-1]]).__path__
#         except AttributeError:
#             continue
#
#         try:
#             imp.find_module(REPORTING_SOURCE_FILE, app_path)
#         except ImportError:
#             continue
#
#         __import__('%s.%s' % (app, REPORTING_SOURCE_FILE))
