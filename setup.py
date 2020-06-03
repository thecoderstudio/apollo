import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'VERSION')) as f:
    version = f.read().strip()

requires = [
    'bcrypt',
    'fastapi',
    'pyjwt',
    'psycopg2',
    'pydantic',
    'sqlalchemy',
]

test_requires = [
    'bcrypt',
    'coverage',
    'pyjwt',
    'pytest',
    'pytest-asyncio',
    'pytest-mock',
    'requests',
    'sqlalchemy_utils'
]

dev_requires = [
    'alembic',
    'uvicorn'
]

extras = {
    'tests': test_requires,
    'dev': dev_requires
}

setup(
    name='apollo',
    version=version,
    author='Code R',
    author_email='hello@coderstudio.nl',
    install_requires=requires,
    tests_require=test_requires,
    extras_require=extras
)
