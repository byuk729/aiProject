from fastapi import FastAPI
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

from llm_pipeline import answer_with_context

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

class GroceryResponse(BaseModel):
    prompt: str
    answer: str
    
@app.get('/')
def root():
    return {"Hello": "World"}

@app.post('/api/grocery-recs', response_model=GroceryResponse)
def create_grocery_recs(prompt: Prompt) -> GroceryResponse:
    # temporary context for testing
    retrieved_context = """
                        Store: Walmart, Item: eggs, Price: 2.49
                        Store: Kroger, Item: eggs, Price: 3.19
                        Store: Kroger, Item: milk, Price: 3.59
                        Store: Walmart, Item: milk, Price: 3.89
                        """

    answer = answer_with_context(prompt.prompt, retrieved_context)

    return GroceryResponse(
        prompt=prompt.prompt,
        answer=answer
    )
