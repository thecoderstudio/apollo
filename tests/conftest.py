from pytest import fixture

import apollo.lib.settings


@fixture
def settings():
    yield apollo.lib.settings.settings
    apollo.lib.settings.settings = {}
