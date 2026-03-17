
from fastapi import FastAPI

app = FastAPI()

usuarios = ['Yuri', 'Rodrigo', 'Hugo']

@app.get("/users/{index}")
async def users(index):
    return {"nome": usuarios[index]}