from apollo.lib.security.cors import get_origins


def test_get_origins(mocker, patched_settings):
    patched_settings['Web'] = {
        'domain': 'localhost',
        'port': '1234'
    }
    mocker.patch('apollo.lib.security.cors.settings', patched_settings)
    origins = get_origins()

    assert origins == (
        'http://localhost:1234',
        'https://localhost:1234'
    )
