from fastapi import FastAPI
from .routers import strategies, broker_accounts

app = FastAPI(title="AgentTrader Strategy Service")

app.include_router(strategies.router)
app.include_router(broker_accounts.router)
