# Apollo
![](https://github.com/thecoderstudio/apollo/workflows/Test/badge.svg)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/2208dfecb4c345f299ca14491905ea37)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=thecoderstudio/apollo&amp;utm_campaign=Badge_Grade)
[![codecov](https://codecov.io/gh/thecoderstudio/apollo/branch/develop/graph/badge.svg?token=3CJ4O4JTUZ)](https://codecov.io/gh/thecoderstudio/apollo)

Apollo is a post-exploitation tool for managing, enumerating and pivotting on
compromised machines.

This app is only meant to be ethically used. Only use Apollo on systems you're
authorized to use.

## Installation & usage
When you run Apollo for the first time, the username and password for the admin user will be logged to the console.

## Configuration
The first step is to rename or copy `local-settings.ini.dist` to `local-settings.ini` in fill in the required settings.

### From source
To install:
```
pip install -e .
```

To run:
```
uvicorn apollo:app --reload
```

To test run in project root directory:
```
pytest
```

### With Docker
Building your development environment with Docker:
```
docker-compose -f dev-compose.yml build --no-cache
```

Running your development environment:
```
docker-compose -f dev-compose.yml up
```

Run tests:
```
docker-compose -f test-compose.yml up --exit-code-from apollo-test apollo-test
```