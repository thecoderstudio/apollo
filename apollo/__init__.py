from fastapi import FastAPI

from apollo.handlers import root

app = FastAPI()

app.include_router(root.router)
