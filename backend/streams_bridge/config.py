import os
from dataclasses import dataclass

@dataclass
class Config:
    database_url: str
    price_stream_url: str | None
    options_flow_url: str | None
    options_flow_api_key: str | None
    news_stream_url: str | None
    news_stream_api_key: str | None
    account_updates_url: str | None
    account_updates_api_key: str | None

def load_config() -> Config:
    return Config(
        database_url=os.environ["DATABASE_URL"],
        price_stream_url=os.environ.get("PRICE_STREAM_URL"),
        options_flow_url=os.environ.get("OPTIONS_FLOW_URL"),
        options_flow_api_key=os.environ.get("OPTIONS_FLOW_API_KEY"),
        news_stream_url=os.environ.get("NEWS_STREAM_URL"),
        news_stream_api_key=os.environ.get("NEWS_STREAM_API_KEY"),
        account_updates_url=os.environ.get("ACCOUNT_UPDATES_URL"),
        account_updates_api_key=os.environ.get("ACCOUNT_UPDATES_API_KEY"),
    )
