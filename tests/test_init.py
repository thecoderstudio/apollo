import pytest

from apollo import (app, configure, main, read_settings_files,
                    add_validation_exception_handler)
from apollo.lib.exceptions.validation import validation_exception_handler
from tests import async_mock


class ConfigParserMock:
    @staticmethod
    def __iter__():
        return iter((('test', 1),))

    @staticmethod
    def read(filename):
        return filename


@pytest.mark.asyncio
async def test_main(mocker):
    configure_mock = mocker.patch('apollo.configure')
    configue_if_needed_mock = mocker.patch('apollo.initialise_if_needed')
    mocker.patch('apollo.app', new=async_mock)

    await main()

    configure_mock.assert_called_once()
    configue_if_needed_mock.assert_called_once()


def test_configure(mocker):
    read_mock = mocker.patch('apollo.read_settings_files')
    init_sqlalchemy_mock = mocker.patch('apollo.init_sqlalchemy')
    add_validation_exception_handler_mock = mocker.patch(
        'apollo.add_validation_exception_handler')

    configure()

    read_mock.assert_called_once()
    init_sqlalchemy_mock.assert_called_once()
    add_validation_exception_handler_mock.assert_called_once()


def test_read_settings_files(mocker, patched_settings):
    mock = mocker.patch('apollo.ConfigParser')
    mock.return_value = ConfigParserMock()

    read_settings_files()

    assert patched_settings == {'test': 1}


def test_add_validation_exception_handler(mocker):
    add_validation_exception_handler()
    assert validation_exception_handler in app.exception_handlers.values()
