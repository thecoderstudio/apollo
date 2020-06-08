from pytest import fixture

from tests.lib.security import get_authorization_policy_with_mock


@fixture(scope='function')
def mock_policy(mocker):
    def generate_policy(provider_acl=[]):
        return get_authorization_policy_with_mock(mocker, provider_acl)
    return generate_policy
