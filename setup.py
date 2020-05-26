import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'VERSION')) as f:
    version = f.read().strip()

requires = [
    'fastapi',
    'uvicorn'
]

test_requires = [
    'coverage',
    'pytest',
    'requests'
]

setup(
    name='apollo',
    version=version,
    author='Code R',
    author_email='hello@coderstudio.nl',
    install_requires=requires,
    tests_require=test_requires
)
