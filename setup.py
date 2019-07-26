#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import io
import os
import sys
from setuptools import find_packages, setup


def read_req(req_file):
    with open(os.path.join('requirements', req_file)) as req:
        return [line.strip() for line in req.readlines() if line.strip() and not line.strip().startswith('#')]


with io.open('README.rst', encoding='utf-8') as readme:
    description = readme.read()
#print(description)
requirements = read_req('base.txt')
print(requirements)
#requirements_validation = read_req('validation.txt')

py3_supported_range = (5, 7)

# convert inclusive range to exclusive range
py3_supported_range = (py3_supported_range[0], py3_supported_range[1] + 1)
python_requires = ", ".join([">=2.7"] + ["!=3.{}.*".format(v) for v in range(0, py3_supported_range[0])])
python_classifiers = [
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
] + ['Programming Language :: Python :: 3.{}'.format(v) for v in range(*py3_supported_range)]


def sparrow_permission_command_setup(**kwargs):
    setup(
        name='sparrow_permission_command',
        version='v1.0',
        packages=find_packages('command'),
        package_dir={'': 'command'},
        include_package_data=True,
        install_requires=requirements,
        license='BSD License',
        description='Sparrow internal use, register APIS to Auth Centre',
        long_description=description,
        url='https://github.com/wangbl11/sparrow_permission_command.git',
        author='tina.wang',
        author_email='wangbl11@qq.com',
        keywords='drf django django-rest-framework schema swagger openapi codegen swagger-codegen '
                 'documentation django-rest-swagger drf-openapi sparrow',
        python_requires=python_requires,
        classifiers=[
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Development Status :: 5 - Production/Stable',
            'Operating System :: OS Independent',
            'Environment :: Web Environment',
            'Framework :: Django',
            'Framework :: Django :: 1.11',
            'Framework :: Django :: 2.0',
            'Framework :: Django :: 2.1',
            'Framework :: Django :: 2.2',
            'Topic :: Documentation',
            'Topic :: Software Development :: Code Generators',
        ] + python_classifiers,
        **kwargs
    )


try:
    sparrow_permission_command_setup()
except Exception as e:
    import traceback
    traceback.print_exc()
    # if os.getenv('CI', 'false') == 'true' or os.getenv('TRAVIS', 'false') == 'true':
    #     # don't silently fail on travis - we don't want to accidentally push a dummy version to PyPI
    #     raise
    #
    # err_msg = str(e)
    # if 'setuptools-scm' in err_msg or 'setuptools_scm' in err_msg:
    #     import time
    #     import traceback
    #
    #     timestamp_ms = int(time.time() * 1000)
    #     timestamp_str = hex(timestamp_ms)[2:].zfill(16)
    #     dummy_version = '1!0.0.0.dev0+noscm.' + timestamp_str
    #
    #     sparrow_permission_command_setup(version=dummy_version)
    #
    #     traceback.print_exc(file=sys.stderr)
    #     print("failed to detect version, package was built with dummy version " + dummy_version, file=sys.stderr)
    # else:
    #     raise
