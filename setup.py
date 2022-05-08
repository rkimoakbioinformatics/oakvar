from setuptools import setup
from setuptools.command.install import install
import sys
import os
import time
import atexit
import traceback
import shutil

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.rst").read_text()

data_files = ['cravat.yml', 
              'cravat-system.template.yml', 
              'modules/cravat.yml', 
              'example_input'
]
for root, dirs, files in os.walk(os.path.join('cravat', 'webviewer')):
    root_files = [os.path.join('..', root, f) for f in files]
    data_files.extend(root_files)
for root, dirs, files in os.walk(os.path.join('cravat', 'liftover')):
    root_files = [os.path.join('..', root, f) for f in files]
    data_files.extend(root_files)
for root, dirs, files in os.walk(os.path.join('cravat', 'annotator_template')):
    root_files = [os.path.join('..', root, f) for f in files]
    data_files.extend(root_files)
for root, dirs, files in os.walk(os.path.join('cravat', 'webresult')):
    root_files = [os.path.join('..', root, f) for f in files]
    data_files.extend(root_files)
for root, dirs, files in os.walk(os.path.join('cravat', 'webstore')):
    root_files = [os.path.join('..', root, f) for f in files]
    data_files.extend(root_files)
for root, dirs, files in os.walk(os.path.join('cravat', 'websubmit')):
    root_files = [os.path.join('..', root, f) for f in files]
    data_files.extend(root_files)
oakvar_files = ['cravat.yml', 
              'cravat-system.template.yml', 
              'modules/cravat.yml', 
              'example_input'
]
for root, dirs, files in os.walk(os.path.join('oakvar', 'webviewer')):
    root_files = [os.path.join('..', root, f) for f in files]
    oakvar_files.extend(root_files)
for root, dirs, files in os.walk(os.path.join('oakvar', 'liftover')):
    root_files = [os.path.join('..', root, f) for f in files]
    oakvar_files.extend(root_files)
for root, dirs, files in os.walk(os.path.join('oakvar', 'annotator_template')):
    root_files = [os.path.join('..', root, f) for f in files]
    oakvar_files.extend(root_files)
for root, dirs, files in os.walk(os.path.join('oakvar', 'webresult')):
    root_files = [os.path.join('..', root, f) for f in files]
    oakvar_files.extend(root_files)
for root, dirs, files in os.walk(os.path.join('oakvar', 'webstore')):
    root_files = [os.path.join('..', root, f) for f in files]
    oakvar_files.extend(root_files)
for root, dirs, files in os.walk(os.path.join('oakvar', 'websubmit')):
    root_files = [os.path.join('..', root, f) for f in files]
    oakvar_files.extend(root_files)
oakvar_files = ['cravat.yml']
setup(
    name='oakvar',
    version='2.3.18',
    description='A genomic variant analysis platform',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/rkimoakbioinformatics/oakvar',
    author='Ryangguk Kim',
    author_email='rkim@oakbioinformatics.com',
    license='MIT',
    classifiers='',
    keywords='genomic variant analysis interpretation genome',
    project_urls={
        'Documentation': 'https://oakvar.readthedocs.io',
        'Source': 'https://github.com/rkimoakbioinformatics/oakvar',
        'Tracker': 'https://github.com/rkimoakbioinformatics/oakvar/issues',
    },
    packages=['cravat', 'oakvar'],
    py_modules=[],
    install_requires=[
        'pyyaml',
        'requests',
        'requests-toolbelt',
        'pyliftover',
        'websockets',
        'markdown',
        'aiohttp',
        'chardet>=3.0.4',
        'aiosqlite',
        'oyaml',
        'intervaltree',
        'xlsxwriter',
        'openpyxl',
        'twobitreader',
        'nest-asyncio',
        'psutil',
        'mpmath',
        'pyvcf',
    ],
    python_requires='>=3.6',
    package_data={
        'cravat': data_files,
        'oakvar': oakvar_files
    },
    data_files=[],
    scripts=[],
    entry_points={
        'console_scripts': [
            'oc=cravat.__main__:main',
            'ov=oakvar.__main__:main',
        ]
    },
)
