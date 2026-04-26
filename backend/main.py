import os
import sys
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
sys.path.append(PROJECT_ROOT)

from llm_pipeline import answer_with_context, semantic_search

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Prompt(BaseModel):
    prompt: str

class GroceryResponse(BaseModel):
    prompt: str
    answer: str
    parsed: dict

@app.get('/')
def root():
    return {"Hello": "World"}

@app.post('/api/grocery-recs', response_model=GroceryResponse)
def create_grocery_recs(prompt: Prompt) -> GroceryResponse:
    retrieved_context = semantic_search(prompt.prompt, top_k=5)
    print(f"[Context] {retrieved_context}")

    if retrieved_context == "No matching products found.":
        return GroceryResponse(
            prompt=prompt.prompt,
            answer="Sorry, I couldn't find any matching products.",
            parsed={}
        )

    # Use first result directly — skip LLM formatting
    answer = retrieved_context
    print(f"[Answer] {answer}")

    return GroceryResponse(
        prompt=prompt.prompt,
        answer=answer,
        parsed={}
    )