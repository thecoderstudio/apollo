from configparser import ConfigParser
from unittest.mock import patch

from apollo.lib.settings import update_settings

config = ConfigParser()
config.read('test.ini')
update_settings(config)


async def async_mock():
    pass


def create_http_connection_mock(cookies={}, headers={}):
    connection_mock = patch('starlette.requests.HTTPConnection')
    connection_mock.cookies = cookies
    connection_mock.headers = headers
    connection_mock.oauth_client = None
    connection_mock.current_user = None
    return connection_mock
