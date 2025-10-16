#!/usr/bin/python

from setuptools import setup, find_packages

entry_points = {
	'console_scripts': [
		'agilepy_spectra = agilepy.api.advanced.spectra.main:main',
    ]
}


setup( name='agilepy',
       version='1.7.0',
       author='Baroncelli Leonardo, Addis Antonio, Bulgarelli Andrea, Parmiggiani Nicolò, Ambra Di Piano, Gabriele Panebianco',
       author_email='leonardo.baroncelli@inaf.it, antonio.addis@inaf.it, andrea.bulgarelli@inaf.it, nicolo.parmiggiani@inaf.it, ambra.dipiano@inaf.it, gabriele.panebianco@inaf.it',
       packages=find_packages(),
       package_dir={ 'agilepy': 'agilepy' },
       scripts=[
          'agilepy/scripts/start_coverage.sh',
          'agilepy/scripts/start_test_rest_api.sh',
          'agilepy/scripts/download_test_dataset.sh',
       ],
       entry_points=entry_points,
       include_package_data=True,
       package_data={'mypkg': [
                         'testing/unittesting/api/conf/*',
                         'testing/unittesting/api/data/*',
                         'testing/unittesting/config/conf/*',
                         'testing/unittesting/core/conf/*',
                         'testing/unittesting/core/test_data/*',
                         'testing/unittesting/utils/conf/*',
                         'testing/unittesting/utils/test_data/*',
                         'utils/AGILE_datacoverage'                         
                    ]},
       license='GPL-3.0'
     )
