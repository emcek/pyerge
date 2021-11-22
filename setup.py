"""Various tools to emerge and to show status for conky."""
import io
from os.path import abspath, dirname, join

from setuptools import setup, find_packages

from pyerge import __version__

here = abspath(dirname(__file__))

with io.open(join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with io.open(join(here, 'requirements.txt'), encoding='utf-8') as f:
    requires = f.read().splitlines()

setup(
    name='pyerge',
    version=__version__,
    description='Various tools to emerge and to show status for conky',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/emcek/pyerge',
    author='Michal Plichta',
    license='GPLv2',
    entry_points={'console_scripts': ['pye = pyerge.cli:run_parser',
                                      'e_sync = pyerge.tools:e_sync',
                                      'e_dl = pyerge.tools:e_dl',
                                      'e_curr = pyerge.tools:e_curr',
                                      'e_eut = pyerge.tools:e_eut',
                                      'e_eta = pyerge.tools:e_eta',
                                      'e_raid = pyerge.tools:run_e_raid',
                                      'glsa = pyerge.glsa:run_glsa']},
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Console',
                 'Environment :: X11 Applications',
                 'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
                 'Operating System :: POSIX',
                 'Operating System :: Unix',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8',
                 'Programming Language :: Python :: 3.9',
                 'Programming Language :: Python :: 3.10',
                 'Topic :: Desktop Environment',
                 'Topic :: Software Development',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'Topic :: System :: Monitoring',
                 'Topic :: Utilities'],
    keywords='gentoo portage emerge conky',
    packages=find_packages(exclude=['tests']),
    install_requires=requires,
    python_requires='>=3.6',
    extras_require={'testing': ['pytest']},
    project_urls={'Bug Reports': 'https://github.com/emcek/pyerge/issues',
                  'Source': 'https://github.com/emcek/pyerge'},
)
