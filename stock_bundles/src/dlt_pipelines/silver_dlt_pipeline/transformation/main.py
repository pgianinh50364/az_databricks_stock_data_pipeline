import sys
sys.path.append("../../silver_dlt_pipeline/utilities")

from pyspark.sql import functions as F
from pyspark.sql.functions import col, when, from_json, to_date, current_timestamp, expr, lit
from pyspark.sql.types import *
from pyspark.sql.window import Window
from pyspark.sql import SparkSession
import pyspark.sql.types as T
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, TimestampType
import dlt

from technical_indicators import TechnicalIndicators

spark = SparkSession.builder.getOrCreate()
spark.conf.set("spark.sql.ansi.enabled", "false")

# Configuration: Set to False to disable streaming and run batch-only
ENABLE_STREAMING = True

#========================
# SILVER LANDING
# + Lightweight cleaning
#========================
@dlt.table(
    name="batch_data",
    comment="Raw ticker data ingested from ADLS"
)
def batch_data():
    base_path = "/Volumes/stock_data_cata/bronze/bronzevolume/"
    folders = [f.name.replace("/", "") for f in dbutils.fs.ls(base_path)]
    df = None

    for folder in folders:
        df_tmp = (
            spark.readStream.format("delta")
            .load(f"{base_path}{folder}/batch_data")
            .withColumn("ticker", F.lit(folder))
        )
        df = df_tmp if df is None else df.unionByName(df_tmp)

    return df

#========================
# SILVER TRANSFORMATION
#========================
silver_rules = {
    "rule1": "date IS NOT NULL",
    "rule2": "ticker IS NOT NULL",
    "rule3": "close > 0",
    "rule4": "year(date) >= 2022",
    "rule5": "volume > 0"
}

@dlt.table(name="silver_cleaned")
@dlt.expect_all(silver_rules)
def silver_cleaned():
    df = dlt.read_stream("batch_data")\
            .withColumn("processed_timestamp", F.current_timestamp())
    return df

@dlt.table(
    name="silver_ticker_indicators",
    comment="Ticker data enriched with technical indicators (batch)"
)
def silver_ticker_indicators():
    df = dlt.read("silver_cleaned")
    ti = (
        TechnicalIndicators(df, symbol_col="ticker", date_col="date")
        .sma()
        .ema()
        .macd()
        .bollinger_bands()
        .atr()
        .rsi()
        .stochastic()
        .cci()
        .mfi()
        .obv()
        .adl()
        .support_resistance()
    )
    df = ti.get_df()
    return df