#!/usr/bin/env python

import astroplant_peripheral_device_library
try:
    from setuptools import setup
except:
    from distutils.core import setup


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='astroplant-peripheral-device-library',
      version=astroplant_peripheral_device_library.__version__,
      description='AstroPlant peripheral device library',
      author='AstroPlant',
      author_email='thomas@kepow.org',
      url='https://astroplant.io',
      packages=['astroplant_peripheral_device_library',],
      install_requires=requirements,
     )

