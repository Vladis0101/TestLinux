from fastapi import FastAPI

app = FastAPI()

@app.get("/", tags=['Привет'])
async def home():
    return {'id':1,'name':'Vasya'}


@app.post("/", tags=['hello1'])
async def add_home():
    return { 'id':2,'name':'Petr'}



# uvicorn Main1:app --host 0.0.0.0 --port 8000 --reload
