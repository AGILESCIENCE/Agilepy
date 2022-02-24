#!/usr/bin/python
# -*- coding: latin-1 -*-

from setuptools import setup, find_packages

setup( name='agilepy',
       version='1.5.0',
       author='Baroncelli Leonardo, Addis Antonio, Bulgarelli Andrea, Parmiggiani Nicolò',
       author_email='leonardo.baroncelli@inaf.it, antonio.addis@inaf.it, andrea.bulgarelli@inaf.it, nicolo.parmiggiani@inaf.it',
       packages=find_packages(),
       package_dir={ 'agilepy': 'agilepy' },
       include_package_data=True,
       license='GPL-3.0'
     )
