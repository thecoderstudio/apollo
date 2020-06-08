from apollo.lib.settings import update_settings


def test_update_settings(patched_settings):
    assert patched_settings == {}

    update_settings({'test': 1})

    assert patched_settings == {'test': 1}
