from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from dataclasses import field, dataclass, asdict
from datetime import date
from dotenv import load_dotenv
from supabase import create_client, Client
import os

load_dotenv()

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")  # Get from .env
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Get from .env

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Define Model
model = GroqModel('llama-3.3-70b-versatile')

@dataclass
class TransactionInput:
    financial_transaction: str

@dataclass
class TransactionOutput:
    type: str = field(metadata={"description": "Type of transaction (credit/debit)"})
    amount: float
    date: date
    category: str

# Create the agent
finance_agent = Agent(
    model=model,
    system_prompt="You are a finance analyser that understands the user's financial transaction and splits it into type, amount, date, and category.",
    result_type=TransactionOutput,
)

# Run the agent
response = finance_agent.run_sync("I paid 220 rs for groceries yesterday")

# Convert dataclass to dictionary and format date
transaction_data = asdict(response.data)
transaction_data["date"] = transaction_data["date"].isoformat()  # Convert date to string

# Insert into Supabase
response = supabase.table("transactions").insert(transaction_data).execute()
print(response)
