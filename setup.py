import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'VERSION')) as f:
    version = f.read().strip()

requires = [
    'aiofiles~=0.6.0',
    'bcrypt~=3.2.0',
    'click~=7.1.2',
    'fastapi~=0.63.0',
    'psycopg2~=2.8.6',
    'pydantic~=1.8.1',
    'pyjwt~=1.7.1',
    'redis~=3.5.3',
    'sqlalchemy~=1.3.24',
    'uvicorn[standard]~=0.13.4'
]

test_requires = [
    'async-asgi-testclient~=1.4.6',
    'coverage~=5.5',
    'pytest~=6.2.3',
    'pytest-asyncio~=0.15.0',
    'pytest-mock~=3.5.1',
    'requests~=2.25.1'
]

dev_requires = [
    'alembic'
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
