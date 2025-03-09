from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from dotenv import load_dotenv
from supabase import create_client, Client
import os
from finance_agent.schema.finance_agent_schema import TransactionOutput
load_dotenv()

class TransactaionAgent:
    def __init__(self):
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY") 

        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        self.model = GroqModel('llama-3.3-70b-versatile')
        self.set_agents()

    def set_agents(self):
        self.finance_agent = Agent(
            model=self.model,
            system_prompt="You are a finance analyser that understands the user's financial transaction and splits it into type, amount, date, and category.",
            result_type=TransactionOutput,
        )

        self.summarizing_agent = Agent(
            model=self.model,
            system_prompt="Summarize all transactions, highlighting spending patterns, major expenses, frequent categories, and unusual trends.",
        )

        self.financial_advice_agent = Agent(
            model=self.model,
            system_prompt="You are a financial advisor. Analyze the user's summarized transactions and provide insights on spending habits, saving potential, and ways to optimize finances.",
        )

    async def insert_transaction(self, transaction: str):
        print("-----started insert")
        response = await self.finance_agent.run(transaction)
        print("-----response: ",response)

        transaction_data = response.data.model_dump()
        print("-----transaction_data: ",transaction_data)
        transaction_data["date"] = transaction_data["date"].isoformat()  # Convert date to string

        response = self.supabase.table("transactions").insert(transaction_data).execute()
        print("-----response: ",response)
        return {"status": "success"} if response else {"status": "failed"}

    async def summarize(self):
        response = self.supabase.table("transactions").select("*").execute()
        transactions = response.data

        transactions_text = "\n".join(
            [f"{t['date']}: {t['type']} {t['amount']} rs for {t['category']} ({t.get('description', '')})"
            for t in transactions]
        )

        summary = await self.summarizing_agent.run(transactions_text)
        print("Summary in: ", summary.data)
        return summary.data

    async def get_advice(self):
        result_summary = await  self.summarize()
        advice = await self.financial_advice_agent.run(result_summary)
        return {"advice":advice.data,"summary":result_summary}