import os
from setuptools import setup, find_packages

install_requires = []
with open('requirements.txt') as reqs:
    for line in reqs.readlines():
        req = line.strip()
        if not req or req.startswith('#'):
            continue
        install_requires.append(req)

setup(
    name='iexplot',
    description='plotting tools for IEX beamline (29ID of the APS)',
    url='https://github.com/apsiex/iexplot',
    maintainer='Jessica McChesney',
    maintainer_email='jmcchesn@anl.gov',
    version='2.0',
    packages=find_packages(),
    install_requires=install_requires,
    scripts=[],
    dependency_links=[],
    package_data={'examples': ['examples/*']}

)
