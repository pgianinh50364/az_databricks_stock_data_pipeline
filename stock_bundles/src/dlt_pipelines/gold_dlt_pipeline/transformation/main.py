import sys
sys.path.append("../../gold_dlt_pipeline/utilities")

from pyspark.sql import functions as F
from pyspark.sql.functions import col, when
from pyspark.sql.types import *
from pyspark.sql.types import IntegerType
from pyspark.sql.window import Window
from pyspark.sql import SparkSession
import dlt

from ticker_info import build_dim_tickers

spark = SparkSession.builder.getOrCreate()

# -----------------------------------
# DIMENSIONS
# -----------------------------------
@dlt.table(
    name="cdc_tickers",
    comment="Information about tickers (static attributes via Yahoo)"
)
def cdc_tickers():
    df = dlt.read("stock_data_cata.silver.silver_cleaned")
    tickers = [row.ticker for row in df.select("ticker").distinct().collect()]
    enriched = build_dim_tickers(spark, tickers)

    return (
        enriched
        .select(
            "ticker",
            "company_name",
            "sector",
            "industry",
            "market_cap",
            "market_cap_category",
            "country",
            "currency",
            "exchange",
        )
        .withColumn("modified_date", F.current_timestamp())
        .withColumn("ticker_key", F.xxhash64("ticker")) # Not actually a key, but useful for CDC
    )

dlt.create_streaming_table(
    name="dim_tickers",
    comment="Track companie's profile"
)

dlt.create_auto_cdc_flow(
    target = "dim_tickers",
    source = "cdc_tickers",
    keys = ["ticker_key"],
    sequence_by = col("modified_date"),
    stored_as_scd_type = 1
)

@dlt.table(name="dim_date")
def dim_date():
    return (
        dlt.read("stock_data_cata.silver.silver_cleaned")
        .select("date")
        .distinct()
        .withColumn("date_key", F.date_format(col("date"), "yyyyMMdd").cast(IntegerType()))
        .withColumn("year", F.year(col("date")))
        .withColumn("month", F.month(col("date")))
        .withColumn("day", F.dayofmonth(col("date")))
        .withColumn("quarter", F.quarter(col("date")))
        .withColumn("day_of_week", F.dayofweek(col("date")))
        .withColumn("day_of_year", F.dayofyear(col("date")))
        .withColumn("week_of_year", F.weekofyear(col("date")))
        .withColumn("month_name", F.date_format(col("date"), "MMMM"))
        .withColumn("day_name", F.date_format(col("date"), "EEEE"))
        .withColumn("is_month_end", when(F.dayofmonth(F.date_add(col("date"), 1)) == 1, True).otherwise(False))
        .withColumn(
            "is_quarter_end",
            when(F.month(col("date")).isin([3, 6, 9, 12]) &
                 (F.dayofmonth(F.date_add(col("date"), 1)) == 1), True).otherwise(False)
        )
    )

# -----------------------------------
# FACT TABLES
# -----------------------------------
ticker_performance_rules = {
    "rule1": "date IS NOT NULL",
    "rule2": "ticker IS NOT NULL",
    "rule3": "close_price > 0",
    "rule4": "volume >= 0"
}

@dlt.table(
    name="fact_daily_ticker_performance",
    comment="Daily ticker performance with technical indicators (batch)"
)
@dlt.expect_all(ticker_performance_rules)
def fact_daily_ticker_performance():
    main = dlt.read("stock_data_cata.silver.silver_ticker_indicators").alias("main")
    dd = dlt.read("dim_date").alias("dd")
    dt = dlt.read("dim_tickers").alias("dt")
    ticker_window = Window.partitionBy(col("main.ticker")).orderBy(col("main.date"))

    base = (
        main.join(dd, col("main.date") == col("dd.date"), "left")
            .join(dt, col("main.ticker") == col("dt.ticker"), "left")
            .select(
                col("dd.date_key"),
                col("dt.ticker_key"),
                F.lit(2).alias("session_id"),
                col("main.date"),
                col("main.ticker"),
                col("main.open").alias("open_price"),
                col("main.high").alias("high_price"),
                col("main.low").alias("low_price"),
                col("main.close").alias("close_price"),
                col("main.volume"),

                # Technical indicators
                col("main.sma_5"),
                col("main.sma_15"),
                col("main.sma_20"),
                col("main.sma_30"),
                col("main.sma_50"),
                col("main.ema_12"),
                col("main.macd"),
                col("main.macd_signal"),
                col("main.macd_gap"),
                col("main.bbands_sma"),
                col("main.bbands_upper"),
                col("main.bbands_lower"),
                col("main.bbands_width"),
                col("main.bbands_pct"),
                col("main.atr"),
                col("main.rsi"),
                col("main.stoch_signal"),
                col("main.cci"),
                col("main.obv"),
                col("main.adl"),
                col("main.mfi"),
                col("main.resistance"),
                col("main.support"),
                col("main.distance_to_resistance"),
                col("main.distance_to_support"),
            )
    )

    # compute derived measures AFTER select to avoid alias scoping issues
    base = base.withColumn(
        "daily_return_pct",
        (col("close_price") - col("open_price")) / col("open_price") * 100.0
    ).withColumn(
        "daily_volatility_pct",
        (col("high_price") - col("low_price")) / col("open_price") * 100.0
    ).withColumn(
        "dollar_volume",
        col("volume") * col("close_price")
    ).withColumn(
        "candle_color",
        when(col("close_price") > col("open_price"), "Green")
        .when(col("close_price") < col("open_price"), "Red")
        .otherwise("Neutral")
    ).withColumn(
        "is_high_volume",
        (col("volume") > F.avg(col("volume")).over(ticker_window.rowsBetween(-19, 0)))
    ).withColumn(
        "rsi_signal",
        when(col("rsi") > 70, "Overbought")
        .when(col("rsi") < 30, "Oversold")
        .otherwise("Normal")
    ).withColumn("created_timestamp", F.current_timestamp()
    ).withColumn("updated_timestamp", F.current_timestamp())

    # Remove manual write - let DLT handle data storage
    return base

@dlt.table(name="fact_weekly_ticker_summary")
def fact_weekly_ticker_summary():
    main = dlt.read("fact_daily_ticker_performance").alias("main")
    dd = dlt.read("dim_date").alias("dd")
    df = (
        main.join(dd, col("main.date_key") == col("dd.date_key"), "left")
            .groupBy(
                col("main.ticker_key"),
                col("main.ticker"),
                col("dd.year"),
                F.weekofyear(col("main.date")).alias("week_of_year")
            )
            .agg(
                F.first("main.open_price").alias("week_open"),
                F.last("main.close_price").alias("week_close"),
                F.max("main.high_price").alias("week_high"),
                F.min("main.low_price").alias("week_low"),
                F.sum("main.volume").alias("week_volume"),
                F.sum("main.dollar_volume").alias("week_dollar_vol"),
                F.avg("main.daily_return_pct").alias("avg_daily_return"),
                F.stddev("main.daily_return_pct").alias("volatility"),
                F.count("*").alias("trading_day"),
                F.sum(when(col("main.candle_color") == "Green", 1).otherwise(0)).alias("green_days"),
                F.sum(when(col("main.candle_color") == "Red", 1).otherwise(0)).alias("red_days"),
                F.current_timestamp().alias("created_timestamp")
            )
            .withColumn("week_return_pct",
                        (col("week_close") - col("week_open")) / col("week_open") * 100.0)
    )

    return df

@dlt.table(name="fact_monthly_ticker_summary")
def fact_monthly_ticker_summary():
    main = dlt.read("fact_daily_ticker_performance").alias("main")
    dd = dlt.read("dim_date").alias("dd")
    df = (
        main.join(dd, col("main.date_key") == col("dd.date_key"), "left")
            .groupBy(
                col("main.ticker_key"),
                col("main.ticker"),
                col("dd.year"),
                col("dd.month")
            )
            .agg(
                F.first("main.open_price").alias("month_open"),
                F.last("main.close_price").alias("month_close"),
                F.max("main.high_price").alias("month_high"),
                F.min("main.low_price").alias("month_low"),
                F.sum("main.volume").alias("month_volume"),
                F.sum("main.dollar_volume").alias("month_dollar_volume"),
                F.avg("main.daily_return_pct").alias("avg_daily_return"),
                F.stddev("main.daily_return_pct").alias("volatility"),
                F.count("*").alias("trading_days"),
                F.avg("main.rsi").alias("avg_rsi"),
                F.last("main.sma_20").alias("final_sma_20"),
                F.last("main.sma_50").alias("final_sma_50"),
                F.current_timestamp().alias("created_timestamp")
            )
            .withColumn("month_return_pct",
                        (col("month_close") - col("month_open")) / col("month_open") * 100.0)
    )

    return df

@dlt.table(
    name="data_quality_metrics",
    comment="Data quality monitoring for the star schema"
)
def data_quality_metrics():

    df = dlt.read("fact_daily_ticker_performance")\
            .groupBy(col("date"))\
            .agg(
                F.count("*").alias("total_records"),
                F.countDistinct("ticker").alias("unique_tickers"),
                F.sum(when(col("volume") == 0, 1).otherwise(0)).alias("zero_volume_records"),
                F.sum(when(col("close_price").isNull(), 1).otherwise(0)).alias("null_price_records"),
                F.avg("volume").alias("avg_volume"),
                F.current_timestamp().alias("calculated_timestamp")
            )
    return df

# -----------------------------------
# ANALYTICAL VIEWS
# -----------------------------------
@dlt.view(name="v_ticker_performance")
def v_ticker_performance():
    main = dlt.read("fact_daily_ticker_performance").alias("main")
    dd = dlt.read("dim_date").alias("dd")
    dt = dlt.read("dim_tickers").alias("dt")
    return (
        main.join(dd, col("main.date_key") == col("dd.date_key"), "left")
            .join(dt, col("main.ticker_key") == col("dt.ticker_key"), "left")
            .where(col("dd.date") >= F.date_sub(F.current_date(), 30))
            .select(
                col("main.ticker"),
                col("dt.sector"),
                col("dt.industry"),
                col("dd.date"),
                col("dd.day_name"),
                col("main.close_price"),
                col("main.daily_return_pct"),
                col("main.volume"),
                col("main.dollar_volume"),
                col("main.rsi"),
                col("main.candle_color"),
                when(col("main.daily_return_pct") > 5, "Strong up")
                    .when(col("main.daily_return_pct") > 2, "Up")
                    .when(col("main.daily_return_pct") > -2, "Flat")
                    .when(col("main.daily_return_pct") > -5, "Down")
                    .otherwise("Strong down").alias("performance_category"),
                when(col("main.rsi") > 70, "Overbought")
                    .when(col("main.rsi") < 30, "Oversold")
                    .otherwise("Neutral").alias("rsi_signal"),
                when(col("main.is_high_volume"), "High Volume").otherwise("Normal").alias("basic_volume_indicator")
            )
    )

@dlt.view(name="v_sector_performance")
def v_sector_performance():
    main = dlt.read("fact_daily_ticker_performance").alias("main")
    dd = dlt.read("dim_date").alias("dd")
    dt = dlt.read("dim_tickers").alias("dt")
    return (
        main.join(dd, col("main.date_key") == col("dd.date_key"), "left")
            .join(dt, col("main.ticker_key") == col("dt.ticker_key"), "left")
            .where(col("dd.date") >= F.date_sub(F.current_date(), 90))
            .groupBy(
                col("dt.sector"),
                col("dd.date"),
                col("dd.year"),
                col("dd.month"),
                col("dd.quarter")
            )
            .agg(
                F.count("main.ticker").alias("num_stocks"),
                F.avg("main.daily_return_pct").alias("avg_sector_return"),
                F.sum("main.dollar_volume").alias("total_dollar_volume"),
                F.avg("main.rsi").alias("avg_rsi"),
                F.stddev("main.daily_return_pct").alias("volatility"),
                F.sum(when(col("main.daily_return_pct") > 0, 1).otherwise(0)).alias("gainers"),
                F.sum(when(col("main.daily_return_pct") < 0, 1).otherwise(0)).alias("losers"),
            )
            .withColumn("gainer_ratio", col("gainers") / col("num_stocks"))
            .withColumn(
                "sector_strength",
                when(col("avg_sector_return") > 2, "Very Strong")
                    .when(col("avg_sector_return") > 0.5, "Strong")
                    .when(col("avg_sector_return") > -0.5, "Neutral")
                    .when(col("avg_sector_return") > -2, "Weak")
                    .otherwise("Very weak")
            )
    )

@dlt.view(name="v_technical_screening")
def v_technical_screening():
    main = dlt.read("fact_daily_ticker_performance").alias("main")
    dd = dlt.read("dim_date").alias("dd")
    dt = dlt.read("dim_tickers").alias("dt")
    window_30d = Window.partitionBy("main.ticker").orderBy("dd.date").rowsBetween(-29, 0)

    return (
        main.join(dd, col("main.date_key") == col("dd.date_key"), "left")
            .join(dt, col("main.ticker_key") == col("dt.ticker_key"), "left")
            .select(
                col("main.ticker"),
                col("dt.sector"),
                col("main.close_price"),
                col("main.volume"),
                col("main.daily_return_pct"),
                col("main.sma_20"),
                col("main.sma_50"),
                col("main.rsi"),
                col("main.macd"),
                col("main.macd_signal"),
                col("main.bbands_pct"),
                col("main.atr"),
                when((col("main.close_price") > col("main.sma_20")) &
                     (col("main.sma_20") > col("main.sma_50")), "Bullish Trend")
                    .when((col("main.close_price") < col("main.sma_20")) &
                          (col("main.sma_20") < col("main.sma_50")), "Bearish Trend")
                    .otherwise("Sideways").alias("trend_signal"),
                when(col("main.macd") > col("main.macd_signal"), "MACD Bullish")
                    .otherwise("MACD Bearish").alias("basic_macd_signal"),
                when(col("main.bbands_pct") > 0.8, "Near Upper BB")
                    .when(col("main.bbands_pct") < 0.2, "Near Lower BB")
                    .otherwise("BB Middle").alias("bb_position"),
                (col("main.rsi") < 30).alias("oversold_flag"),
                (col("main.rsi") > 70).alias("overbought_flag"),
                (col("main.volume") > F.avg(col("main.volume")).over(window_30d) * 2).alias("volume_spike_flag"),
                (col("main.daily_return_pct") > 5).alias("strong_mover_flag")
            )
    )

@dlt.view(
    name="v_risk_metrics",
    comment="risk analysis and portfolio metrics"
)
def v_risk_metrics():
    main = dlt.read("fact_monthly_ticker_summary").alias("main")
    dt = dlt.read("dim_tickers").alias("dt")
    return (
        main.join(dt, col("main.ticker_key") == col("dt.ticker_key"), "left")
            .where(col("main.year") >= F.year(F.date_sub(F.current_date(), 365)))
            .select(
                col("main.ticker"),
                col("dt.sector"),
                col("main.year"),
                col("main.month"),
                col("main.month_return_pct"),
                col("main.volatility").alias("month_volatility"),
                col("main.avg_daily_return"),
                col("main.trading_days"),
                (col("main.month_return_pct") / col("main.volatility")).alias("risk_adjusted_return"),
                when(col("main.volatility") < 15, "Low risk")
                    .when(col("main.volatility") < 25, "Medium risk")
                    .otherwise("High risk").alias("risk_category"),
                when(col("main.month_return_pct") > 10, "Excellent")
                    .when(col("main.month_return_pct") > 5, "Good")
                    .when(col("main.month_return_pct") > 0, "Positive")
                    .when(col("main.month_return_pct") > -5, "Slight loss")
                    .otherwise("Poor").alias("performance_rating")
            )
    )

# -----------------------------------
# BUSINESS KPIs
# -----------------------------------
@dlt.view(
    name="v_kpi_daily_market_health",
    comment="Daily KPIs for overall market health assessment"
)
def v_kpi_daily_market_health():
    main = dlt.read("fact_daily_ticker_performance").alias("main")
    dd = dlt.read("dim_date").alias("dd")
    return (
        main.join(dd, col("main.date_key") == col("dd.date_key"), 'left')
            .groupBy(col("main.date"))
            .agg(
                F.count("main.ticker").alias("total_stocks_traded"),
                F.sum("main.dollar_volume").alias("total_market_volume"),
                F.avg("main.daily_return_pct").alias("market_avg_return"),
                F.stddev("main.daily_return_pct").alias("market_volatility"),
                F.sum(when(col("main.daily_return_pct") > 0, 1).otherwise(0)).alias("gainers"),
                F.sum(when(col("main.daily_return_pct") < 0, 1).otherwise(0)).alias("losers"),
                F.sum(when(col("main.daily_return_pct") == 0, 1).otherwise(0)).alias("unchanged"),
                F.avg("main.rsi").alias("avg_market_rsi"),
                F.sum(when(col("main.rsi") > 70, 1).otherwise(0)).alias("overbought_count"),
                F.sum(when(col("main.rsi") < 30, 1).otherwise(0)).alias("oversold_count"),
                F.sum(when(col("main.is_high_volume"), 1).otherwise(0)).alias("high_volume_count"),
                F.sum(when(col("main.daily_return_pct") > 5, 1).otherwise(0)).alias("strong_gainers"),
                F.sum(when(col("main.daily_return_pct") < -5, 1).otherwise(0)).alias("strong_losers"),
                F.current_timestamp().alias("calculated_timestamp")
            )
            .withColumn("advance_decline_ratio", col("gainers") / col("losers"))
            .withColumn(
                "market_sentiment",
                when(col("advance_decline_ratio") > 2, "Very bullish")
                    .when(col("advance_decline_ratio") > 1.5, "Bullish")
                    .when(col("advance_decline_ratio") > 0.67, "Neutral")
                    .when(col("advance_decline_ratio") > 0.5, "Bearish")
                    .otherwise("Very bearish")
            )
            .withColumn(
                "volatility_regime",
                when(col("market_volatility") > 3, "High volatility")
                    .when(col("market_volatility") > 1.5, "Normal volatility")
                    .otherwise("Low volatility")
            )
    )