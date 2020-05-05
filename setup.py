from setuptools import find_packages, setup

__version__ = "0.1"

PACKAGE = "covid-dashboard"

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f]

setup(
    name=PACKAGE,
    version=__version__,
    packages=find_packages(exclude=["tests", "notebooks"]),
    install_requires=requirements,
    entry_points={"console_scripts": ["update_covid = covid.cli:main"]},
)
