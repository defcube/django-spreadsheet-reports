import logging
import datetime

from django.db.models import Sum
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

import django_spreadsheet_reports
from django_spreadsheet_reports.models import Notice


logger = logging.getLogger(__name__)


def save_reports(report_type='daily', should_send_mail=True):
    logger.info("Getting %s reports" % report_type)
    if report_type == 'daily':
        cutoff = datetime.date.today() - datetime.timedelta(days=2)
        reports = django_spreadsheet_reports.site.get_daily_reports()
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
    elif report_type == 'weekly':
        cutoff = datetime.date.today() - datetime.timedelta(days=8)
        reports = django_spreadsheet_reports.site.get_weekly_reports()
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        two_weeks = datetime.date.today() - datetime.timedelta(days=15)
    else:
        logger.error("%s is not a valid report type" % report_type)
        raise RuntimeError()
    count = 0
    for report in reports:
        logger.info("Getting stats for report %s" % report.name)
        qs = report.notice_model.objects.filter(**report.notices_filter_by)
        if report_type == 'daily':            
            qs = qs.filter(date=yesterday).values(
                report.notice_group_by).annotate(Sum(report.notice_field))
        elif report_type == 'weekly':
            qs = qs.filter(date__lte=yesterday, date__gte=cutoff).values(
                report.notice_group_by).annotate(Sum(report.notice_field))

        for row in qs:
            high_limit = low_limit = 0
            group_by = row[report.notice_group_by]
            val = float(row[report.notice_field+'__sum'])
            if report_type == 'daily':
                filters = {report.notice_group_by: group_by,
                           'date': cutoff}
            elif report_type == 'weekly':
                # noinspection PyUnboundLocalVariable
                filters = {report.notice_group_by: group_by,
                           'date__lte': cutoff,
                           'date__gte': two_weeks}
            else:
                raise RuntimeError()
            old_mark = report.notice_model.objects.filter(
                **report.notices_filter_by).filter(
                **filters).values(report.notice_group_by).annotate(
                Sum(report.notice_field))
        
            is_visible = True
            prev_val = 0.0
            if old_mark:
                mark = old_mark[0]
                prev_val = float(mark[report.notice_field+'__sum'])
                logger.info("Got prev_val of %s" % prev_val)
                high_limit = prev_val + (prev_val * report.change_threshold)
                low_limit = prev_val - (prev_val * report.change_threshold)
                if low_limit <= val <= high_limit:
                    is_visible = False
            if val < report.minimum_threshold and \
               prev_val < report.minimum_threshold:
                is_visible = False
                
            if is_visible:
                Notice.objects.create(slug=report.slug,
                                      group_name=group_by,
                                      group_val=val,
                                      prev_val=prev_val,
                                      low_limit=low_limit,
                                      high_limit=high_limit)
            logger.info("Created notice for %s" % group_by)
            count += 1
        logger.info("Created %s notices" % count)


def send_new_notices_report():
    logger.info("sending email to staff members")
    subject = 'New notices report'
    cutoff = datetime.datetime.now() - datetime.timedelta(hours=24)
    notices = Notice.objects.filter(creation_date__gte=cutoff)
    staff_members = []  # TODO make this a list of staff usernames
    message = render_to_string('django_spreadsheet_reports/notice_list.txt',
                               {'notices': notices})
    logger.info("sending emails to %s staff members" % len(staff_members))
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, staff_members,
              fail_silently=False)
    logger.info("finished")


def load_from_urls():
    from django.conf import settings
    __import__(settings.ROOT_URLCONF)
