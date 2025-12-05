from fastapi import FastAPI
from .routers import strategies, broker_accounts, paper_orders, trades

app = FastAPI(title="AgentTrader Strategy Service")

app.include_router(strategies.router)
app.include_router(broker_accounts.router)
app.include_router(paper_orders.router)
app.include_router(trades.router)
