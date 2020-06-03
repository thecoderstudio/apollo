from configparser import ConfigParser

from apollo.lib.settings import update_settings


def init_test_database():
    config = ConfigParser()
    config.read('test.ini')
    update_settings(config)

init_test_database()

async def async_mock():
    pass

