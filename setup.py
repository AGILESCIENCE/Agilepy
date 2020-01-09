#!/usr/bin/python
# -*- coding: latin-1 -*-

from setuptools import setup, find_packages

requires = [
    'pyyaml'
]

setup( name='Agilepy',
       version='0.0.0',
       install_requires=requires,
       author='Addis Antonio, Baroncelli Leonardo, Parmiggiani Nicolò',
       author_email='antonio.addis@inaf.it leonardo.baroncelli@inaf.it, nicolo.parmiggiani@inaf.it',
       packages=["api", "config", "dataclasses", "utils"],
       package_dir = {
           "api" : "agilepy/api",
           "config" : "agilepy/config",
           "dataclasses" : "agilepy/dataclasses",
           "utils" : "agilepy/utils"
       }   
       
        
     )
