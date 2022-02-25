#!/usr/bin/python

from setuptools import setup, find_packages

setup( name='agilepy',
       version='1.5.0',
       author='Baroncelli Leonardo, Addis Antonio, Bulgarelli Andrea, Parmiggiani Nicolò',
       author_email='leonardo.baroncelli@inaf.it, antonio.addis@inaf.it, andrea.bulgarelli@inaf.it, nicolo.parmiggiani@inaf.it',
       packages=find_packages(),
       package_dir={ 'agilepy': 'agilepy' },
       scripts=[
          'agilepy/scripts/start_agilepy_notebooks.sh',
          'agilepy/scripts/start_container.sh',
          'agilepy/scripts/start_coverage_local.sh',
          'agilepy/scripts/start_coverage.sh',
          'agilepy/scripts/start_notebooks_docker.sh'
       ],
       include_package_data=True,
       package_data={'mypkg': [
                         'testing/unittesting/api/conf/*',
                         'testing/unittesting/api/data/*',
                         'testing/unittesting/config/conf/*',
                         'testing/unittesting/core/conf/*',
                         'testing/unittesting/core/test_data/*',
                         'testing/unittesting/utils/conf/*',
                         'testing/unittesting/utils/test_data/*'                         
                    ]},
       license='GPL-3.0'
     )