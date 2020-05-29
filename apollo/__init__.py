from configparser import ConfigParser

from fastapi import FastAPI

from apollo.handlers import root, user, auth
from apollo.lib.settings import update_settings
from apollo.models import init_sqlalchemy

app = FastAPI()

app.include_router(root.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.on_event('startup')
async def configure():
    read_settings_files()
    init_sqlalchemy()


def read_settings_files():
    config = ConfigParser()
    config.read('settings.ini')
    config.read('local-settings.ini')
    update_settings(config)
