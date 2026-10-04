from fastapi import FastAPI

app = FastAPI(title="Favorites API")

@app.get("/")
def hello():
    return {"message": "hello world"}