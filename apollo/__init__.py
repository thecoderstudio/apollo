from configparser import ConfigParser

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apollo.handlers import agent, auth, oauth, root, user, websocket
from apollo.lib.initialisation import initialise_if_needed
from apollo.lib.redis import RedisSession
from apollo.lib.security.cors import get_origins
from apollo.lib.settings import settings, update_settings
from apollo.models import init_sqlalchemy

app = FastAPI()

app.include_router(agent.router)
app.include_router(auth.router)
app.include_router(oauth.router)
app.include_router(root.router)
app.include_router(user.router)
app.include_router(websocket.router)


async def main(*args, **kwargs):
    configure()
    initialise_if_needed()
    return await app(*args, **kwargs)


def configure():
    read_settings_files()
    init_sqlalchemy()
    add_cors()
    init_cache()
    add_validation_exception_handler()


def add_cors():
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_origins(),
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )


def init_cache():
    redis_settings = settings['redis']
    lifetime = redis_settings.pop('default_ttl_in_seconds')
    redis_session = RedisSession(lifetime)
    redis_session.configure(**redis_settings)


def add_validation_exception_handler():
    from apollo.lib.exceptions import validation  # noqa


def read_settings_files():
    config = ConfigParser()
    config.read('settings.ini')
    config.read('local-settings.ini')
    update_settings(config)
