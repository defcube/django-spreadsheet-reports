from django.conf.urls import patterns, url
from django.contrib.admin.views.decorators import staff_member_required
from django.template import RequestContext
from django.shortcuts import render_to_response

from . import models


@staff_member_required
def home(request):
    context = RequestContext(request)
    context['available_reports'] = site._registered_reports
    context['bookmarks'] = models.Bookmark.objects.all()
    context['daily_reports'] = site._registered_daily_reports
    context['weekly_reports'] = site._registered_weekly_reports
    return render_to_response('django_spreadsheet_reports/home.html', context_instance=context)


def wrap(report):
    def wrapper(request, *args, **kwargs):
        return report.render_to_response(request)

    wrapper = staff_member_required(wrapper)
    return wrapper


class ReportingSite(object):
    _registered_reports = []
    _registered_daily_reports = []
    _registered_weekly_reports = []

    def register(self, report):
        if isinstance(report, type):
            report = report()
        self._registered_reports.append(report)

    def register_daily(self, report):
        if isinstance(report, type):
            report = report()
        self._registered_daily_reports.append(report)

    def get_daily_reports(self):
        return self._registered_daily_reports

    def register_weekly(self, report):
        if isinstance(report, type):
            report = report()
        self._registered_weekly_reports.append(report)

    def get_weekly_reports(self):
        return self._registered_weekly_reports

    def urls(self):
        urlpatterns = patterns('', url(r'^$', home, name='django_spreadsheet_reports'))
        for report in self._registered_reports:
            urlpatterns += patterns('', url(r'^%s/$' % report.slug, wrap(report),
                                            name='django_spreadsheet_reports-%s' % report.slug))
        for report in self._registered_daily_reports:
            urlpatterns += patterns('', url(r'^%s/$' % report.slug, wrap(report),
                                            name='django_spreadsheet_reports-%s' % report.slug))
        for report in self._registered_weekly_reports:
            urlpatterns += patterns('', url(r'^%s/$' % report.slug, wrap(report),
                                            name='django_spreadsheet_reports-%s' % report.slug))
        return urlpatterns

    urls = property(urls)
site = ReportingSite()
