from apollo.lib.security import AuthorizationPolicy


def get_acl_provider_mock(mocker, acl):
    return mocker.MagicMock(
        __acl__=mocker.MagicMock(return_value=acl)
    )


def get_authorization_policy_with_mock(mocker, acl=[]):
    return AuthorizationPolicy(get_acl_provider_mock(mocker, acl))
