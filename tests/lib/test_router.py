import pytest

from apollo.lib.exceptions import HTTPException
from apollo.lib.router import SecureRouter
from apollo.lib.security import Allow, Agent


@pytest.mark.parametrize("permission,auth_header,permitted", [
    ('public', None, True),
    ('public', '', True),
    ('public', 'fake', True),
    ('test', None, False),
    ('test', '', False),
    ('test', 'fake', False),
    ('test',
     "Bearer b8887eefe2179eccb0565674fe196ee12f0621d1d2017a61b195ec17e5d2ac57",
     True)
])
@pytest.mark.asyncio
async def test_websocket_oauth_permissions(mocker, db_session, access_token,
                                           permission, auth_header, permitted):
    access_token.access_token = (
        "b8887eefe2179eccb0565674fe196ee12f0621d1d2017a61b195ec17e5d2ac57"
    )
    db_session.commit()

    router = SecureRouter([(Allow, Agent, 'test')])

    @router.websocket_('/test', permission=permission)
    async def mock(websocket):
        pass

    websocket_mock = mocker.MagicMock()
    websocket_mock.headers = {
        'authorization': auth_header
    }

    if permitted:
        await mock(websocket_mock)
    else:
        with pytest.raises(HTTPException, match="Permission denied."):
            await mock(websocket_mock)
