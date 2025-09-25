from pyspark.sql.window import Window
from pyspark.sql.functions import col, avg, lag, when
from pyspark.sql import functions as F
from pyspark.sql.types import *

class TechnicalIndicators:
    def __init__(self, df, symbol_col="symbol", date_col="date"):
        self.df = df
        self.symbol_col = symbol_col
        self.date_col = date_col
        self.w = Window.partitionBy(self.symbol_col).orderBy(self.date_col)
    
    # ========================
    # Trend Indicators
    # ========================
    def sma(self, col="close", periods=[5, 15, 20, 30, 50]):
        for p in periods:
            w = self.w.rowsBetween(-(p-1), 0)
            self.df = self.df.withColumn(f"sma_{p}", F.avg(col).over(w))
        return self

    def ema(self, col="close", span=12, out_col="ema_12"):
        alpha = 2.0 / (span + 1)
        w = self.w.rowsBetween(-(span-1), 0)
        
        sma = F.avg(col).over(w)
        self.df = self.df.withColumn(
            out_col, F.lit(0)
        )
        prev_ema = F.lag(out_col, 1).over(self.w)
        
        # EMA formula: EMA = alpha * current_price + (1-alpha) * previous_EMA
        self.df = self.df.withColumn(
            out_col, 
            F.when(F.isnull(prev_ema), sma)
            .otherwise(alpha * F.col(col) + (1-alpha) * prev_ema)
        )
        return self
    def macd(self, col="close", fast=12, slow=26, signal=9):
        w_fast = self.w.rowsBetween(-(fast-1), 0)
        w_slow = self.w.rowsBetween(-(slow-1), 0)
        self.df = (
            self.df
            .withColumn("ema_fast", F.avg(col).over(w_fast))
            .withColumn("ema_slow", F.avg(col).over(w_slow))
        )
        self.df = self.df.withColumn("macd", F.col("ema_fast") - F.col("ema_slow"))
        w_sig = self.w.rowsBetween(-(signal-1), 0)
        self.df = self.df.withColumn("macd_signal", F.avg("macd").over(w_sig))
        self.df = self.df.withColumn("macd_gap", F.col("macd") - F.col("macd_signal"))
        return self
    
    # ========================
    # Volatility Indicators
    # ========================
    def bollinger_bands(self, col="close", period=20, num_std=2):
        w = self.w.rowsBetween(-(period-1), 0)
        sma = F.avg(col).over(w)
        std = F.stddev(col).over(w)
        self.df = self.df.withColumn("bbands_sma", sma)
        self.df = self.df.withColumn("bbands_upper", sma + num_std * std)
        self.df = self.df.withColumn("bbands_lower", sma - num_std * std)
        self.df = self.df.withColumn("bbands_width", F.col("bbands_upper") - F.col("bbands_lower"))
        self.df = self.df.withColumn("bbands_pct", (F.col(col) - F.col("bbands_lower"))/(F.col("bbands_upper") - F.col("bbands_lower")))
        return self

    def atr(self, period=14):
        self.df = (
            self.df.withColumn("prev_close", F.lag("close").over(self.w))
            .withColumn("tr", F.greatest(
                F.col("high") - F.col("low"),
                F.abs(F.col("high") - F.col("prev_close")),
                F.abs(F.col("low") - F.col("prev_close"))
            ))
        )
        w = self.w.rowsBetween(-(period-1), 0)
        self.df = self.df.withColumn("atr", F.avg("tr").over(w))
        return self
    
    # ========================
    # Momentum Indicators
    # ========================
    def rsi(self, col="close", period=14):
        delta = F.col(col) - F.lag(col).over(self.w)
        self.df = (
            self.df
            .withColumn("delta", delta)
            .withColumn("gain", F.when(delta > 0, delta).otherwise(0))
            .withColumn("loss", F.when(delta < 0, -delta).otherwise(0))
        )
        w = self.w.rowsBetween(-(period-1), 0)
        self.df = (
            self.df
            .withColumn("avg_gain", F.avg("gain").over(w))
            .withColumn("avg_loss", F.avg("loss").over(w))
            .withColumn("rs", F.col("avg_gain") / F.col("avg_loss"))
            .withColumn("rsi", 100 - (100 / (1 + F.col("rs"))))
        )
        return self

    def stochastic(self, period=14):
        w = self.w.rowsBetween(-(period-1), 0)
        self.df = (
            self.df
            .withColumn("lowest_low", F.min("low").over(w))
            .withColumn("highest_high", F.max("high").over(w))
            .withColumn("stoch_oscillator",
                        (F.col("close") - F.col("lowest_low")) /
                        (F.col("highest_high") - F.col("lowest_low")) * 100)
        )
        self.df = self.df.withColumn("stoch_signal", F.avg("stoch_oscillator").over(w))
        return self
    
    def cci(self, period=20):
        tp = (F.col("high") + F.col("low") + F.col("close")) / 3
        w = self.w.rowsBetween(-(period-1), 0)
        sma_tp = F.avg(tp).over(w)
        md = F.avg(F.abs(tp - sma_tp)).over(w)
        self.df = self.df.withColumn("cci", (tp - sma_tp) / (0.015 * md))
        return self
    
    def mfi(self, period=14):
        tp = (F.col("high") + F.col("low") + F.col("close")) / 3
        money_flow = tp * F.col("volume")
        delta_tp = tp - F.lag(tp).over(self.w)
        pos_flow = F.when(delta_tp > 0, money_flow).otherwise(0)
        neg_flow = F.when(delta_tp < 0, money_flow).otherwise(0)
        self.df = (
            self.df
            .withColumn("pos_flow", pos_flow)
            .withColumn("neg_flow", neg_flow)
        )
        w = self.w.rowsBetween(-(period-1), 0)
        self.df = (
            self.df
            .withColumn("pos_mf", F.sum("pos_flow").over(w))
            .withColumn("neg_mf", F.sum("neg_flow").over(w))
            .withColumn("mfi", 100 - (100 / (1 + (F.col("pos_mf") / F.col("neg_mf")))))
        )
        return self
    
    # ========================
    # Volume Indicators
    # ========================
    def obv(self, period=50):
        w_o = self.w.rowsBetween(-(period-1), 0)
        delta = F.col("close") - F.lag("close").over(self.w)
        obv_val = F.when(delta > 0, F.col("volume")) \
                   .when(delta < 0, -F.col("volume")) \
                   .otherwise(0)
        self.df = self.df.withColumn("obv", F.sum(obv_val).over(w_o))
        return self

    def adl(self, period=50):
        w_a = self.w.rowsBetween(-(period-1), 0)
        mfm = ((F.col("close") - F.col("low")) - (F.col("high") - F.col("close"))) / (F.col("high") - F.col("low"))
        mfv = mfm * F.col("volume")
        self.df = self.df.withColumn("adl", F.sum(mfv).over(w_a))
        return self
    
    # ========================
    # Custom Indicators
    # ========================
    def support_resistance(self, period=20):
        w = self.w.rowsBetween(-(period-1), 0)
        self.df = (
            self.df
            .withColumn("resistance", F.max("high").over(w))
            .withColumn("support", F.min("low").over(w))
            .withColumn("distance_to_resistance", (F.col("resistance") - F.col("close")) / F.col("close"))
            .withColumn("distance_to_support", (F.col("close") - F.col("support")) / F.col("close"))
        )
        return self
    
    # ========================
    # Finalize
    # ========================
    def get_df(self):
        return self.df