import datetime
import dateutil.parser
import re


class ParseError(RuntimeError): 
    pass


class TextDateRange(object):
    """
    >>> TextDateRange('2008-04-01').tuple()
    ('2008-04-01', '2008-04-01')
    
    >>> TextDateRange('2008-4-1').tuple()
    ('2008-04-01', '2008-04-01')

    >>> TextDateRange('2008-04-01').num_days()
    1

    >>> TextDateRange('2008-04-01:2008-04-03').tuple()
    ('2008-04-01', '2008-04-03')

    >>> TextDateRange('2008-04-01:2008-04-03').num_days()
    3
    
    >>> TextDateRange('2007-12-29:2008-01-02').days_list()
    ['2007-12-29', '2007-12-30', '2007-12-31', '2008-01-01', '2008-01-02']

    >>> TextDateRange('2008-04-01:2008-04-03', set_end_date_time=True).tuple()
    ('2008-04-01', '2008-04-03 23:59:59')

    >>> TextDateRange('2008-04-01:2008-04-03', set_end_date_time=True).num_days()
    3

    >>> TextDateRange('2007-12-29:2008-01-02', set_end_date_time=True).days_list()
    ['2007-12-29', '2007-12-30', '2007-12-31', '2008-01-01', '2008-01-02']

    >>> TextDateRange('abc')
    Traceback (most recent call last):
      ...
    ParseError: Unable to parse date "abc"

    >>> TextDateRange('2008-04-03:2008-03-01')
    Traceback (most recent call last):
      ...
    ParseError: Enddate must be after the startdate
    """
    def __init__(self, instr, set_end_date_time=False):
        tokens = instr.split(':')
        try:
            date_strings = [self._token_to_date_string(x) for x in tokens]
            if len(date_strings) == 1:
                self.start, self.end = date_strings[0], date_strings[0]
            elif len(date_strings) == 2:
                self.start, self.end = date_strings[0], date_strings[1]
            else:
                raise ParseError
        except ParseError:
            raise ParseError('Unable to parse date "%s"' % instr)
        if self.start > self.end:
            raise ParseError('Enddate must be after the startdate')
        if set_end_date_time:
            self.end += ' 23:59:59'
    
    def _token_to_date_string(self, token):
        daysagoregex = re.compile(r'(\d+) ?days ?ago')
        dateregex = re.compile('^(\d{4})-(\d{1,2})-(\d{1,2})$')
        if token.lower() == 'yesterday':
            return self._format_datetime(datetime.datetime.today() - datetime.timedelta(days=1))
        elif token.lower() == 'today':
            return self._format_datetime(datetime.datetime.today())
        elif daysagoregex.match(token.lower()):
            days_ago = int(daysagoregex.match(token.lower()).groups()[0])
            return self._format_datetime(datetime.datetime.today() - datetime.timedelta(days=days_ago))
        elif dateregex.match(token):
            groups = dateregex.match(token).groups()
            return "%04d-%02d-%02d" % (int(groups[0]), int(groups[1]), int(groups[2]))
        else:
            raise ParseError
        
    def _set_start_end_from_days_ago(self, days_ago):
            date = self._format_datetime(datetime.datetime.today() - datetime.timedelta(days=days_ago))
            self.start, self.end = date, date
        
    def days_list(self):
        format = '%Y-%m-%d'
        date = datetime.datetime.strptime(self.start, format)
        enddate = datetime.datetime.strptime(_strip_time(self.end), format)
        increment_by = datetime.timedelta(days=1)
        output = []
        while date <= enddate:
            output.append(self._format_datetime(date))
            date += increment_by
        return output
    
    def tuple(self):
        return (self.start, self.end)

    def num_days(self):
        d1 = datetime.datetime.strptime(_strip_time(self.end), '%Y-%m-%d')
        d2 = datetime.datetime.strptime(self.start, '%Y-%m-%d')
        return (d1 - d2).days + 1

    @property
    def start_dateobj(self):
        return dateutil.parser.parse(self.start)

    @property
    def end_dateobj(self):
        return dateutil.parser.parse(self.end)
    
    def _format_datetime(self, datetime):
        format = '%Y-%m-%d'
        return datetime.strftime(format)

    def __str__(self):
        return "{0} -> {1}".format(self.start, self.end)


def _strip_time(date_with_time):
    return date_with_time.split(' ')[0]
        

if __name__ == '__main__':
    import doctest
    print("Running doctest . . .")
    doctest.testmod()