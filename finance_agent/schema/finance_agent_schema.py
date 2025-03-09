
from datetime import date
from pydantic import BaseModel, Field


class TransactionInput(BaseModel):
    financial_transaction: str

class TransactionOutput(BaseModel):
    type: str = Field(description="Type of transaction (credit/debit)")
    amount: float
    date: date
    category: str