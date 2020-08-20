from inspect import Parameter

import pytest

from apollo.lib.signature import check_parameter_has_default


@pytest.mark.parametrize("parameter, expected_outcome", [
    (Parameter(
        'test',
        Parameter.POSITIONAL_OR_KEYWORD,
        default='test'
    ), True),
    (Parameter(
        'test',
        Parameter.POSITIONAL_OR_KEYWORD,
        default=Parameter.empty
    ), False)
])
def test_check_parameter_has_default(parameter, expected_outcome):
    assert check_parameter_has_default(parameter) == expected_outcome
