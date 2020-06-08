from pytest import fixture

from tests.lib.security import (
    get_acl_provider_mock, get_authorization_policy_with_mock)


@fixture
def mock_policy(mocker):
    def generate_policy(provider_acl=[]):
        return get_authorization_policy_with_mock(mocker, provider_acl)
    return generate_policy


@fixture
def mock_context_acl_provider(mocker):
    def generate_context_acl_provider(acl=[]):
        return get_acl_provider_mock(mocker, acl)
    return generate_context_acl_provider
