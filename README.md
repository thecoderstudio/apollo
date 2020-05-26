# Apollo
Apollo is a post-exploitation tool for managing, enumerating and pivotting on
compromised machines.

This app is only meant to be ethically used. Only use Apollo on systems you're
authorized to use.

## Installation & usage
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
