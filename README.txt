I was heavily inspired by http://code.google.com/p/django-reporting/. After playing
with django-reporting, I was wishing parts of it were implemented differently. And so,
django-spreadsheet-reports was born.

Although this project has been in development for a few years, it's documentation is very light.

A few features provided by this are:

* Ability to produce spreadsheet reports off of a user model by creating a reports.py in your app
  directories. The contents of the reports.py should look like:

  class UserStatsReport(django_spreadsheet_reports.Report):
    name = 'Simple User Report'
    slug = 'simple-user-report'
    model = UserStats

    filter_by = django_spreadsheet_reports.filters(
        django_spreadsheet_reports.DateFilter('user__date_joined'),
        django_spreadsheet_reports.Filter('user__date_joined', name='Days', multiple=True),
        )

    group_by = django_spreadsheet_reports.groupbys(
        'user__date_joined',
        django_spreadsheet_reports.GroupBy('campaign__user__username',  name='Affiliate'),
        django_spreadsheet_reports.GroupBy('program__name',  name='Program'),
        django_spreadsheet_reports.GroupBy('referring_url',  name='Referring URL'),
        django_spreadsheet_reports.GroupBy('track__track',  name='Track'),
        django_spreadsheet_reports.GroupBy('tour__name',  name='Tour',
                           additional_columns=[
                               django_spreadsheet_reports.Column('tour__url', name='Tour URL'),
                               django_spreadsheet_reports.Column('tour__program__name', name='Program'),
                               ]),
    )

    list_aggregates = django_spreadsheet_reports.columns(
        django_spreadsheet_reports.Column(Count('id'), name='Members'),

* Exporting to CSV is built in
* Sortable columns

Requirements: Python>=3.4, Django>=1.5

Installation
=============
* pip install django-spreadsheet-reports
* Add `django_spreadsheet_reports` to your installed apps
* Add to your urls file: url(r'^reports/', include(django_spreadsheet_reports.site.urls)),
* Create a reports.py in one of your app directories, and add a Report subclass in it.
* Register your report subclass, by adding a line like this to the bottom of your reports
    file: django_spreadsheet_reports.site.register(UserStatsReport)
