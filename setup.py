#!/usr/bin/python
# -*- coding: latin-1 -*-

from setuptools import setup, find_packages

requires = [
    'pyyaml'
]

setup( name='Agilepy',
       version='25-1.0.0',
       install_requires=requires,
       author='Baroncelli Leonardo, Addis Antonio, Bulgarelli Andrea, Parmiggiani Nicolò',
       author_email='antonio.addis@inaf.it, andrea.bulgarelli@inaf.it, leonardo.baroncelli@inaf.it, nicolo.parmiggiani@inaf.it',
       packages=find_packages(),
       package_dir={ 'agilepy': 'agilepy' }
     )
