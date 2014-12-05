import logging
from optparse import make_option

import lockfile
from django.core.management import base
from django.db import transaction

from django_spreadsheet_reports.utils import save_reports, load_from_urls


logger = logging.getLogger(__name__)


class Command(base.NoArgsCommand):
    option_list = base.NoArgsCommand.option_list + (
        make_option('-s', action='store_true', dest='silentmode',
                    default=False, help='Run in silent mode'),
        make_option('--debug', action='store_true',
                    dest='debugmode', default=False,
                    help='Debug mode (overrides silent mode)'),
    )

    @transaction.commit_on_success
    def handle_noargs(self, **options):
        if not options['silentmode']:
            logging.getLogger('djangoproject').setLevel(logging.INFO)
        if options['debugmode']:
            logging.getLogger('djangoproject').setLevel(logging.DEBUG)
        lock = lockfile.FileLock('/tmp/django_spreadsheet_reports_update_weekly_notes')
        lock.acquire(10)
        with lock:
            load_from_urls()
            save_reports(report_type='weekly')
