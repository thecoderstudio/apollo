from inspect import signature, Parameter

import pytest

from apollo.lib.signature import check_parameter_has_default, copy_parameters


def method_with_no_params():
    pass


def method_with_no_default_params(a, b):
    pass


def method_with_default_params(a, b, c=1):
    pass


def source_method(d, e, f=2):
    pass


@pytest.mark.parametrize(
    "to_signature, keys, expected_keys",
    [
        (signature(method_with_default_params), [], ['a', 'b', 'c']),
        (signature(method_with_default_params), ['d', 'e', 'f'],
         ['e', 'd', 'a', 'b', 'c', 'f']),
        (signature(method_with_no_default_params), ['f'], ['a', 'b', 'f']),
        (signature(method_with_no_params), ['d'], ['d'])
    ]
)
def test_copy_parameters(to_signature, keys, expected_keys):
    from_signature = signature(source_method)
    new_signature = copy_parameters(from_signature, to_signature, keys)
    new_keys = list(new_signature.parameters)
    assert new_keys == expected_keys


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
