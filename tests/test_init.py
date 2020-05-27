from fastapi import FastAPI

from apollo import configure, main, read_settings_files


class ConfigParserMock:
    @staticmethod
    def __iter__():
        return iter((('test', 1),))

    @staticmethod
    def read(filename):
        return filename


def test_main(mocker):
    configure_mock = mocker.patch('apollo.configure')

    app = main()

    configure_mock.assert_called_once()
    assert isinstance(app, FastAPI)


def test_configure(mocker):
    read_mock = mocker.patch('apollo.read_settings_files')
    init_sqlalchemy_mock = mocker.patch('apollo.init_sqlalchemy')

    configure()

    read_mock.assert_called_once()
    init_sqlalchemy_mock.assert_called_once()


def test_read_settings_files(mocker, settings):
    mock = mocker.patch('apollo.ConfigParser')
    mock.return_value = ConfigParserMock()

    read_settings_files()

    assert settings == {'test': 1}
