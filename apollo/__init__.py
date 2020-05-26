from fastapi import FastAPI

app = FastAPI()

from apollo.handlers.root import *  # noqa
