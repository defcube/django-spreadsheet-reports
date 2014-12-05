import datetime

from django import template
from django_spreadsheet_reports.models import Notice


register = template.Library()


def easy_tag(func):
    """
    Decorator to facilitate template tag creation

    deal with the repetitive parts of parsing template tags
    """

    def inner(parser, token):
        # print token
        try:
            return func(*token.split_contents())
        except TypeError:
            raise template.TemplateSyntaxError(
                'Bad arguments for tag "%s"' % token.split_contents()[0])

    inner.__name__ = func.__name__
    inner.__doc__ = inner.__doc__
    return inner


class AppendGetNode(template.Node):
    def __init__(self, d):
        self.dict_pairs = []
        for pair in d.split(','):
            pair = pair.split('=')
            row = (pair[0], template.Variable(pair[1]))
            self.dict_pairs.append(row)

    def render(self, context):
        get = context['request'].GET.copy()
        for key, value in self.dict_pairs:
            get[key] = value.resolve(context)
        path = context['request'].META['PATH_INFO']
        if len(get):
            path += "?%s" % get.urlencode()
        return path


@register.tag()
@easy_tag
def append_to_get(_tag_name, d):
    return AppendGetNode(d)


@register.simple_tag
def display_column(table, value, counter):
    key = list(table.columns._columns.keys())[counter]
    if hasattr(table.columns[key].column, 'choices'):
        d = dict(table.columns[key].column.choices)
        if value is None:
            return 'None'
        return d[value]
    return value


@register.inclusion_tag('django_spreadsheet_reports/notice_list.html')
def show_notice_list(hours_ago=72):
    cutoff = datetime.datetime.now() - datetime.timedelta(hours=hours_ago)
    notices = Notice.objects.filter(
        creation_date__gte=cutoff).order_by('-id')
    return {'notices': notices}
