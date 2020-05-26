import pkg_resources

from fastapi import FastAPI

version = pkg_resources.require('apollo')[0].version
app = FastAPI()

from apollo.handlers.root import *  # noqa
