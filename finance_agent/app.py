from fastapi import FastAPI

from finance_agent.agent import TransactaionAgent

app = FastAPI()

@app.get("/insert")
async def insert_transaction(transaction: str):
    agent = TransactaionAgent()
    response = await agent.insert_transaction(transaction)
    return response

@app.get("/advise")
async def get_advise():
    agent = TransactaionAgent()
    response = await agent.get_advice()
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)