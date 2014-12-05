#!/usr/bin/env python
from distutils.core import setup
# from setuptools import find_packages


readme = open('README.txt').read()

from pip.req import parse_requirements
install_reqs = parse_requirements('requirements.txt')
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='django-spreadsheet-reports',
    version='0.01.4',
    author_email='gattster@gmail.com',
    author='Philip Gatt',
    description="Automates the tasks of producing simple reports from Django models.",
    long_description=readme,
    url='http://github.com/defcube/django-spreadsheet-reports',
    # packages=find_packages(),  #['django_spreadsheet_reports'],
    packages=['django_spreadsheet_reports', 'django_spreadsheet_reports.management.commands',
              'django_spreadsheet_reports.migrations', 'django_spreadsheet_reports.templatetags'],
    include_package_data=True,
    package_dir={'django_spreadsheet_reports': 'django_spreadsheet_reports'},
    package_data={'django_spreadsheet_reports': [
        'templates/admin/*', 'templates/django_spreadsheet_reports/*']},
    data_files=[('', ['README.txt', 'requirements.txt'])],
    install_requires=reqs,
)