#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='wssh',
    version='0.1.0',
    author='Jeff Lindsay',
    author_email='jeff.lindsay@twilio.com',
    description='command-line websocket client+server shell',
    packages=find_packages(),
    install_requires=['ws4py',],
    data_files=[],
    entry_points={
        'console_scripts': [
            'wssh = wssh:main',]},
)
