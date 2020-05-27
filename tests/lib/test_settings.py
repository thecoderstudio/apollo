from apollo.lib.settings import update_settings


def test_update_settings(settings):
    assert settings == {}

    update_settings({'test': 1})

    assert settings == {'test': 1}
