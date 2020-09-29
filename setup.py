import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'VERSION')) as f:
    version = f.read().strip()

requires = [
    'aiofiles',
    'bcrypt',
    'click',
    'fastapi',
    'psycopg2',
    'pydantic',
    'pyjwt',
    'redis',
    'sqlalchemy',
    'uvicorn[standard]'
]

test_requires = [
    'async-asgi-testclient',
    'coverage',
    'pytest',
    'pytest-asyncio',
    'pytest-mock',
    'requests'
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
