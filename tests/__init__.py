from configparser import ConfigParser
import logging


from apollo import app
from apollo.models import init_sqlalchemy, get_connection_url, SessionLocal, get_session, Base, save
from apollo.models.user import User

from sqlalchemy import create_engine
from sqlalchemy_utils.functions import database_exists, create_database

from apollo.lib.settings import update_settings, settings

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from apollo.lib.settings import settings

from pytest import fixture

log = logging.getLogger(__name__)


def init_test_database():
    config = ConfigParser()
    config.read('test.ini')
    update_settings(config)

init_test_database()