from covert import app


@app.get("/")
def get_root():
    return {'version': '0.1'}
