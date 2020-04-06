# -*- coding: utf-8 -*-
"""
setuptools script.

Author:
    Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='etcdgo',
    version='1.0',
    description='A library to push/pull configurations inside etcd databases',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Andrea Cervesato',
    author_email='andrea.cervesato@mailbox.org',
    url='https://github.com/acerv/etcdgo',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
    ],
    packages=["etcdgo"],
    python_version=">3.4,<3.9",
    install_requires=[
        'python-etcd',
        'pyyaml',
        'flatten-dict'
    ],
)
