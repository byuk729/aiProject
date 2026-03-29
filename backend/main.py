from fastapi import FastAPI
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Prompt(BaseModel):
    prompt: str = None
    
@app.get('/')
def root():
    return {"Hello": "World"}

@app.post('/api/grocery-recs')
def create_grocery_recs(prompt: Prompt) -> Prompt:
    return prompt
