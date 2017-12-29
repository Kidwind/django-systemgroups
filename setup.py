#!/usr/bin/env python
from setuptools import setup


VERSION = '1.1.1'

setup(
    name='django-systemgroups',
    version=VERSION,
    url='https://github.com/Kidwind/django-systemgroups',
    author='Kidwind',
    author_email='Kidwind@gmail.com',
    description="基于Django实现的系统组。",
    zip_safe=False,
    packages=[
        'systemgroups',
        'systemgroups.migrations',
    ],
    keywords='django system groups',
    license='BSD',
    classifiers=['Development Status :: 3 - Alpha',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Security',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 ],
)