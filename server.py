from fastapi import FastAPI
from pydantic import BaseModel
from team import initv2m
import uvicorn


app = FastAPI()
class Query(BaseModel):
    question: str
v2m_team = initv2m()

@app.get("/")
async def read_root():
    return {"message": "Hello, AGNO!"}

@app.post("/query")
async def get_response(query: Query):
    print(query)
    response_text = ""
    for response in v2m_team.ask(query.question):
        response_text += response  #
    print(response_text.strip())
    return response_text.strip()

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
