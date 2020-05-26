from fastapi import FastAPI

app = FastAPI()

from covert.handlers.root import *  # noqa
