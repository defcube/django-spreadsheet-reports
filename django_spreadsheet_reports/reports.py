import django.forms
from django.http import HttpResponse


class RepChoiceField(django.forms.fields.ChoiceField):
    def validate(self, value):
        """
        Validates that the input is in self.choices.
        """
        pass


class _NamedValueObject(object):
    def __init__(self, value, name=None):
        if not name:
            if hasattr(value, 'default_alias'):
                name = value.default_alias
            else:
                name = str(value).title()
        self.name = name
        self.value = value


class Filter(_NamedValueObject):
    _is_a_filter = True

    def __init__(self, value, name=None, display_value=None, multiple=False,
                 order=None):
        _NamedValueObject.__init__(self, value, name)
        self.display_value = display_value
        self.multiple = multiple
        self.order = order if order else value

    def filter_choices(self, qs):
        from django.db.models import Count


        values = [self.value]
        if self.display_value:
            values.append(self.display_value)
        xlist = qs.values(*values).annotate(Count('id'))
        if self.order:
            xlist = xlist.order_by(self.order)
        res = [('', '---')]
        for x in xlist:
            if self.display_value:
                res.append((x[self.value], x[self.display_value]))
            else:
                res.append((x[self.value], x[self.value]))
        return res

    def filter_query_set(self, qs, request):
        if self.multiple:
            val = request.GET.getlist(self.name)
            if len(val) == 0 or "" in val:
                return qs
            val = [x for x in val if x.strip() != '']
            if len(val) == 0:
                return qs
            else:
                include_none = False
                if 'None' in val:
                    val.remove('None')
                    include_none = True
                if len(val):
                    args = {'%s__in' % self.value: val}
                    qs = qs.filter(**args)
                if include_none:
                    args = {'%s__isnull' % self.value: True}
                    qs = qs.filter(**args)
                return qs
        else:
            val = request.GET.get(self.name, '')
            if val == '':
                return qs
            else:
                args = {self.value: val}
                return qs.filter(**args)


class BooleanFilter(_NamedValueObject):
    _is_a_filter = True
    multiple = False

    @property
    def _choicelist(self):
        choicelist = ['------', 'True', 'False']
        return choicelist

    def __init__(self, value, name=None):
        _NamedValueObject.__init__(self, value, name)

    def filter_choices(self, qs):
        res = []
        for x in self._choicelist:
            res.append((x, x))
        return res

    def filter_query_set(self, qs, request):
        try:
            val = request.GET[self.name]
        except KeyError:
            val = self._choicelist[0]
        if val == '------' or val == '':
            return qs
        boolval = True
        if val == 'True':
            boolval = True
        if val == 'False':
            boolval = False
        args = {'%s' % self.value: boolval}
        return qs.filter(**args)


class DateFilter(_NamedValueObject):
    _is_a_filter = True
    multiple = False

    @property
    def _choicelist(self):
        choicelist = ['10daysago:today', 'today', 'yesterday', '2daysago', '3daysago', '4daysago',
                      '5daysago', '6daysago', '7daysago', '90daysago:today', 'all time']
        import datetime


        n = datetime.datetime.now()
        for i in range(12):
            n = n.replace(day=1)
            nextmonth = n + datetime.timedelta(days=31)
            lastdayofmonth = nextmonth.replace(day=1) - datetime.timedelta(days=1)
            choicelist.append(
                '{0}-{1:02}-16:{0}-{1:02}-{2:02}'.format(n.year, n.month, lastdayofmonth.day))
            choicelist.append('{0}-{1:02}-01:{0}-{1:02}-15'.format(n.year, n.month))
            choicelist.append(
                '{0}-{1:02}-01:{0}-{1:02}-{2:02}'.format(n.year, n.month, lastdayofmonth.day))
            n = n - datetime.timedelta(days=1)
        return choicelist

    def __init__(self, value, name=None):
        _NamedValueObject.__init__(self, value, name)

    def filter_choices(self, qs):
        res = []
        for x in self._choicelist:
            res.append((x, x))
        return res

    def filter_query_set(self, qs, request):
        from .textdaterange import TextDateRange
        try:
            val = request.GET[self.name]
        except KeyError:
            val = self._choicelist[0]
        if val == 'all time':
            return qs
        daterange = TextDateRange(val)
        args = {'%s__range' % self.value: (daterange.start, daterange.end)}
        return qs.filter(**args)


def filters(*values):
    result = []
    for x in values:
        if not hasattr(x, '_is_a_filter'):
            x = Filter(x)
        result.append(x)
    return result


class Column(_NamedValueObject):
    exists_in_db = True

    def _make_django_tables_column_kwargs(self):
        return dict(verbose_name=self.name)

    def make_django_tables_column(self):
        import django_tables2
        return django_tables2.Column(**self._make_django_tables_column_kwargs())


class CalculatedColumn(Column):
    exists_in_db = False

    def _make_django_tables_column_kwargs(self):
        vals = Column._make_django_tables_column_kwargs(self)
        vals.update(dict(data=self.value))
        return vals


class HiddenColumn(Column):
    exists_in_db = True

    def make_django_tables_column(self):
        import django_tables2
        return django_tables2.Column(visible=False,
                                    **self._make_django_tables_column_kwargs())


class ChoicesColumn(Column):
    exists_in_db = True

    def __init__(self, choices, *args, **kwargs):
        self.choices = choices
        super(ChoicesColumn, self).__init__(*args, **kwargs)

    def make_django_tables_column(self):
        import django_tables2
        a = django_tables2.Column(**self._make_django_tables_column_kwargs())
        a.choices = self.choices
        return a


class DecimalColumn(CalculatedColumn):
    class DecimalFloat():
        def __init__(self, val, decimal_places):
            self.val = val
            self.decimal_places = decimal_places

        def __str__(self):
            format = '%.' + str(self.decimal_places) + 'f'
            return format % self.val

    def __init__(self, val, decimal_places=2, *args, **kwargs):
        def _datafunc(row):
            data = row.data[val]
            if data is None:
                data = 0
            data = float(data)
            return self.DecimalFloat(data, decimal_places)

        CalculatedColumn.__init__(self, _datafunc, *args, **kwargs)


class PercentageCalculatedColumn(CalculatedColumn):
    class PercentFloat(float):
        def __str__(self):
            return '{0:.1%}'.format(self)

    class NullPercent(float):
        def __init__(self):
            float.__init__(-999)

        def __str__(self):
            return '--'

    def __init__(self, top, bottom, *args, **kwargs):
        def _datafunc(row):
            top_data = float(row.data[top])
            bottom_data = float(row.data[bottom])
            if 0 == bottom_data:
                return self.NullPercent()
            else:
                return self.PercentFloat(top_data / bottom_data)

        CalculatedColumn.__init__(self, _datafunc, *args, **kwargs)


class PercentageDifferenceColumn(CalculatedColumn):
    exists_in_db = False

    class PercentFloat(float):
        def __str__(self):
            return '{0:.1%}'.format(self)

    class NullPercent(float):
        def __init__(self):
            float.__init__(-999)

        def __str__(self):
            return '--'

    def __init__(self, before, after, *args, **kwargs):
        def _datafunc(row):
            before_data = float(row.data[before])
            after_data = float(row.data[after])
            delta = after_data - before_data
            if before_data == 0.0:
                return self.PercentFloat(after_data)
            else:
                return self.PercentFloat(delta / before_data)

        CalculatedColumn.__init__(self, _datafunc, *args, **kwargs)


def columns(*values):
    result = []
    for x in values:
        if not isinstance(x, Column):
            x = Column(x)
        result.append(x)
    return result


class GroupBy(_NamedValueObject):
    def __init__(self, value, name=None, additional_columns=None, order=None):
        _NamedValueObject.__init__(self, value, name)
        if additional_columns:
            # when changing code, be careful this does not result in an infinte loop
            self.additional_columns = columns(*additional_columns)
        else:
            self.additional_columns = tuple()
        self.order = order


def groupbys(*values):
    result = []
    for x in values:
        if not isinstance(x, GroupBy):
            x = GroupBy(x)
        result.append(x)
    return result


class Report(object):
    slug = None
    name = None
    model = None
    group_by = []
    list_aggregates = []
    filter_by = []
    order_by = []

    def render_to_response(self, request):
        from django import shortcuts, template
        from . import models


        context = template.RequestContext(request)
        formclass = self.get_form_class(request)
        if request.GET.get('form_submitted'):
            params = request.GET
        else:
            params = formclass.initial_values.copy()
        context['form'] = formclass(params)
        if context['form'].is_valid():
            context['table'] = self.get_data_table(context['form'], request.GET.get('sort', None),
                                                   request)
        context['report_name'] = self.name
        context['request'] = request
        context['bookmarks'] = models.Bookmark.objects.all()
        if request.GET.get('submit') == 'Export to CSV':
            return self._data_table_to_csv(context['table'], self.name)
        else:
            return shortcuts.render_to_response('django_spreadsheet_reports/report.html',
                                                context_instance=context)

    def _data_table_to_csv(self, data_table, name='Report', dialect='excel'):
        """
        Given a data table (or any object that contains an iterable 'columns'
        and 'rows' attribute), returns an HttpResponse containing the data
        serialized into a CSV file.
        """
        import csv

        res = HttpResponse(mimetype='text/csv')
        res['content-disposition'] = 'attachment; filename="%s.csv"' % name

        # even though Columns and Rows are iterable, we must cast them to lists
        # because the python csv writer loops over them using __len__ (which
        # isn't implemented), and __getattr__ (which doesn't accept indexes)

        writer = csv.writer(res, dialect=dialect)
        writer.writerow(list(data_table.columns))
        writer.writerows(list(row) for row in data_table.rows)

        return res

    def get_query_set(self):
        return self.model.objects

    def get_filtered_query_set(self, request):
        qs = self.get_query_set()
        for x in self.filter_by:
            qs = x.filter_query_set(qs, request)
        return qs

    def get_data_table(self, form, sort, request):
        if not form.is_valid():
            raise AssertionError(form.errors)
        annotate = {}
        for v in self.list_aggregates:
            if v.exists_in_db:
                annotate[v.name] = v.value
        groupby = self._get_current_group_by(form)
        values = [groupby.value]
        for x in groupby.additional_columns:
            if x.exists_in_db:
                values.append(x.value)
        qs = self.get_filtered_query_set(request)
        if groupby.order:
            qs = qs.order_by(groupby.order)
        else:
            qs = qs.order_by(groupby.value)
        data = qs.values(*values).annotate(**annotate)
        kwargs = {}
        if sort:
            kwargs['order_by'] = sort
        return self.get_table_class(form)(list(data), **kwargs)

    def _get_current_group_by(self, form):
        groupbystr = form.cleaned_data['group_by']
        for x in self.group_by:
            if x.name == groupbystr:
                return x
        raise KeyError("Group by '%s' cannot be found" % groupbystr)

    def get_table_class(self, form):
        import django_tables2
        properties = {}
        groupby = self._get_current_group_by(form)
        properties[groupby.value] = django_tables2.Column(verbose_name=groupby.name)
        for x in groupby.additional_columns:
            properties[x.value] = x.make_django_tables_column()
        for x in self.list_aggregates:
            properties[x.name] = x.make_django_tables_column()
        return type('Mytable', (django_tables2.Table,), properties)

    def get_form_class(self, request):
        from django import forms
        properties = {}
        properties['form_submitted'] = forms.fields.BooleanField(widget=forms.widgets.HiddenInput)
        properties['initial_values'] = {'group_by': self.group_by[0].name, 'form_submitted': '1'}
        properties['group_by'] = forms.fields.ChoiceField(
            choices=[(x.name, x.name) for x in self.group_by])
        qs = self.get_filtered_query_set(request)
        for x in self.filter_by:
            choices = x.filter_choices(qs)
            c = forms.fields.MultipleChoiceField if x.multiple else RepChoiceField
            properties[x.name] = c(choices=choices, required=False)
            properties['initial_values'][x.name] = choices[0][0]

        if self.order_by:
            choices = []
            for c in self.order_by:
                choices.append((c, c + ' (ASC)'))
                choices.append(('-' + c, c + ' (DESC)'))
            properties['sort'] = RepChoiceField(choices=choices, required=False)
        return type('Myform', (forms.Form,), properties)

    def url(self):
        from django.core import urlresolvers
        return urlresolvers.reverse('django_spreadsheet_reports-%s' % self.slug)

