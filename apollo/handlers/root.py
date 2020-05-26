from apollo import app, version


@app.get("/")
def get_root():
    return {'version': version}
