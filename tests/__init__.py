from configparser import ConfigParser

from apollo.lib.settings import update_settings

config = ConfigParser()
config.read('test.ini')
update_settings(config)


async def async_mock():
    pass
