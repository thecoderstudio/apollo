import pytest

from apollo.lib.exceptions import HTTPException


raisesHTTPForbidden = pytest.raises(HTTPException, match="Permission denied.")
