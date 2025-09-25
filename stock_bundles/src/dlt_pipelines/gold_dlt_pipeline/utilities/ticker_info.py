import yfinance as yf
import pandas as pd
from pyspark.sql import SparkSession

# -----------------------------------
# Market cap categorization
# -----------------------------------
def categorize_market_cap(market_cap: int) -> str:
    if market_cap is None or market_cap == 0:
        return "Unknown"
    elif market_cap >= 200_000_000_000:
        return "Mega Cap"
    elif market_cap >= 10_000_000_000:
        return "Large Cap"
    elif market_cap >= 2_000_000_000:
        return "Mid Cap"
    elif market_cap >= 300_000_000:
        return "Small Cap"
    else:
        return "Micro Cap"


# -----------------------------------
# Fetch metadata
# -----------------------------------
def get_ticker_info(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info or {}

        return {
            "ticker": ticker,
            "company_name": info.get("longName", "Unknown"),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "market_cap": info.get("marketCap", 0),
            "market_cap_category": categorize_market_cap(info.get("marketCap", 0)),
            "country": info.get("country", "Unknown"),
            "currency": info.get("currency", "USD"),
            "exchange": info.get("exchange", "Unknown"),
        }
    except Exception as e:
        # Graceful fallback in case Yahoo Finance fails
        return {
            "ticker": ticker,
            "company_name": "Unknown",
            "sector": "Unknown",
            "industry": "Unknown",
            "market_cap": 0,
            "market_cap_category": "Unknown",
            "country": "Unknown",
            "currency": "USD",
            "exchange": "Unknown",
            "error": str(e),
        }


# -----------------------------------
# Batch enrichment
# -----------------------------------
def build_dim_tickers(spark: SparkSession, tickers: list):
    """
    Given a list of tickers, fetch metadata from Yahoo Finance
    and return a Spark DataFrame suitable for dim_tickers.
    """
    if not tickers:
        # Return empty DF with correct schema
        schema = "ticker STRING, company_name STRING, sector STRING, industry STRING, market_cap LONG, market_cap_category STRING, country STRING, currency STRING, exchange STRING"
        return spark.createDataFrame([], schema)

    # Fetch all ticker metadata
    records = [get_ticker_info(t) for t in tickers]

    # Convert to Pandas → Spark
    pdf = pd.DataFrame(records)
    return spark.createDataFrame(pdf)
