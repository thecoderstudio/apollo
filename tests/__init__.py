# from configparser import ConfigParser
# import logging



# from apollo import app
# from apollo.models import init_sqlalchemy, get_connection_url, SessionLocal, get_session, Base, save
# from apollo.models.user import User

# from sqlalchemy import create_engine
# from sqlalchemy_utils.functions import database_exists, create_database

# from apollo.lib.settings import update_settings, settings

# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# from apollo.lib.settings import settings

# from pytest import fixture

# log = logging.getLogger(__name__)

# @fixture(scope='session', autouse=True)
# def init_test_database():
#     config = ConfigParser()
#     config.read('test.ini')
#     update_settings(config)

#     engine = create_engine(get_connection_url(settings))
#     SessionLocal.configure(bind=engine)
#     Base.metadata.bind = engine

#     if not database_exists(engine.url):    
#         create_database(engine.url)
    
#     Base.metadata.create_all()

#     user = User(
#         username="johndoe", 
#         password_hash='$2b$12$q2ro/WdYipnZxYbPcjWgvuYB4aBI/JVYtPyroXs4SvvcS77p9Mwu2',
#         password_salt='$2b$12$q2ro/WdYipnZxYbPcjWgvu'
#     )

#     save(user)
#     yield
#     Base.metadata.drop_all()


    


# # init_test_database()




