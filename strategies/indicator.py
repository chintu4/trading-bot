

def calculate_indicators(df,SMA_PERIOD=10,RSI_PERIOD=10):
    df["ask_price"] = pd.to_numeric(df["ask_price"], errors='coerce')
    df["sma"] = df["ask_price"].rolling(window=SMA_PERIOD).mean()
    delta = df["ask_price"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=RSI_PERIOD).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=RSI_PERIOD).mean()
    rs = gain / loss if loss.all() != 0 else 0
    df["rsi"] = 100 - (100 / (1 + rs))
    return df

# === CHECK TREND AND RSI ===
def check_trend_and_rsi(df,SMA_PERIOD=10):
    "use calculate_indicators(df) with ask and bid value then pass the same df in check_tread and rsi"
    if len(df) < SMA_PERIOD:
        return False, False, False
    is_uptrend = df["ask_price"].iloc[-1] > df["sma"].iloc[-1]
    rsi = df["rsi"].iloc[-1]
    is_overbought = rsi > 70
    is_oversold = rsi < 30
    return is_uptrend, is_overbought, is_oversold


import pandas as pd
import numpy as np

# === SIMPLE MOVING AVERAGE (SMA) ===
def calculate_sma(df, period=14, column="close"):
    """
    Calculate the Simple Moving Average (SMA).

    Args:
        df (pd.DataFrame): DataFrame containing price data.
        period (int): The period for the SMA calculation.
        column (str): The column name for the price data (default is "close").

    Returns:
        pd.Series: A Pandas Series containing the SMA values.

    Hint:
        - Use SMA to identify the overall trend direction.
        - Commonly used as a baseline for other indicators.

    Why:
        - SMA smooths out price data to identify trends.
        - Helps filter out short-term fluctuations.

    Where:
        - Use in trend-following strategies (e.g., buy when price crosses above SMA).
    """
    return df[column].rolling(window=period).mean()


# === EXPONENTIAL MOVING AVERAGE (EMA) ===
def calculate_ema(df, period=14, column="close"):
    """
    Calculate the Exponential Moving Average (EMA).

    Args:
        df (pd.DataFrame): DataFrame containing price data.
        period (int): The period for the EMA calculation.
        column (str): The column name for the price data (default is "close").

    Returns:
        pd.Series: A Pandas Series containing the EMA values.

    Hint:
        - EMA gives more weight to recent prices, making it more responsive than SMA.

    Why:
        - Useful for identifying short-term trends and momentum.

    Where:
        - Use in momentum-based strategies (e.g., buy when EMA crosses above a longer EMA).
    """
    return df[column].ewm(span=period, adjust=False).mean()


# === RELATIVE STRENGTH INDEX (RSI) ===
def calculate_rsi(df, period=14, column="close"):
    """
    Calculate the Relative Strength Index (RSI).

    Args:
        df (pd.DataFrame): DataFrame containing price data.
        period (int): The period for the RSI calculation.
        column (str): The column name for the price data (default is "close").

    Returns:
        pd.Series: A Pandas Series containing the RSI values.

    Hint:
        - RSI ranges from 0 to 100. Values above 70 indicate overbought conditions, and below 30 indicate oversold.

    Why:
        - Helps identify overbought or oversold conditions.

    Where:
        - Use in mean-reversion strategies (e.g., sell when RSI > 70, buy when RSI < 30).
    """
    delta = df[column].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


# === MOVING AVERAGE CONVERGENCE DIVERGENCE (MACD) ===
def calculate_macd(df, fast_period=12, slow_period=26, signal_period=9, column="close"):
    """
    Calculate the Moving Average Convergence Divergence (MACD).

    Args:
        df (pd.DataFrame): DataFrame containing price data.
        fast_period (int): The period for the fast EMA.
        slow_period (int): The period for the slow EMA.
        signal_period (int): The period for the signal line.
        column (str): The column name for the price data (default is "close").

    Returns:
        pd.DataFrame: A DataFrame containing MACD, Signal Line, and MACD Histogram.

    Hint:
        - MACD is calculated as the difference between the fast and slow EMA.
        - The Signal Line is the EMA of the MACD.

    Why:
        - Helps identify changes in momentum and trend direction.

    Where:
        - Use in crossover strategies (e.g., buy when MACD crosses above the Signal Line).
    """
    fast_ema = calculate_ema(df, period=fast_period, column=column)
    slow_ema = calculate_ema(df, period=slow_period, column=column)
    macd = fast_ema - slow_ema
    signal_line = macd.ewm(span=signal_period, adjust=False).mean()
    macd_histogram = macd - signal_line
    return pd.DataFrame({"MACD": macd, "Signal Line": signal_line, "MACD Histogram": macd_histogram})


# === BOLLINGER BANDS ===
def calculate_bollinger_bands(df, period=20, column="close"):
    """
    Calculate Bollinger Bands.

    Args:
        df (pd.DataFrame): DataFrame containing price data.
        period (int): The period for the Bollinger Bands calculation.
        column (str): The column name for the price data (default is "close").

    Returns:
        pd.DataFrame: A DataFrame containing Upper Band, Middle Band (SMA), and Lower Band.

    Hint:
        - Bollinger Bands consist of a middle band (SMA) and two outer bands (standard deviations).

    Why:
        - Helps identify volatility and potential overbought/oversold conditions.

    Where:
        - Use in volatility-based strategies (e.g., buy when price touches the lower band, sell when it touches the upper band).
    """
    sma = calculate_sma(df, period=period, column=column)
    std = df[column].rolling(window=period).std()
    upper_band = sma + (2 * std)
    lower_band = sma - (2 * std)
    return pd.DataFrame({"Upper Band": upper_band, "Middle Band": sma, "Lower Band": lower_band})


# === AVERAGE TRUE RANGE (ATR) ===
def calculate_atr(df, period=14):
    """
    Calculate the Average True Range (ATR).

    Args:
        df (pd.DataFrame): DataFrame containing price data with columns "high", "low", and "close".
        period (int): The period for the ATR calculation.

    Returns:
        pd.Series: A Pandas Series containing the ATR values.

    Hint:
        - ATR measures market volatility by considering the range between high and low prices.

    Why:
        - Helps set stop-loss levels and assess market volatility.

    Where:
        - Use in volatility-based strategies or to determine position sizing.
    """
    high_low = df["high"] - df["low"]
    high_close = np.abs(df["high"] - df["close"].shift())
    low_close = np.abs(df["low"] - df["close"].shift())
    true_range = np.maximum(high_low, np.maximum(high_close, low_close))
    return true_range.rolling(window=period).mean()


# === STOCHASTIC OSCILLATOR ===
def calculate_stochastic_oscillator(df, period=14, smooth_k=3, smooth_d=3):
    """
    Calculate the Stochastic Oscillator.

    Args:
        df (pd.DataFrame): DataFrame containing price data with columns "high", "low", and "close".
        period (int): The period for the Stochastic Oscillator calculation.
        smooth_k (int): Smoothing period for %K.
        smooth_d (int): Smoothing period for %D.

    Returns:
        pd.DataFrame: A DataFrame containing %K and %D.

    Hint:
        - %K is the current closing price relative to the high-low range.
        - %D is the moving average of %K.

    Why:
        - Helps identify overbought/oversold conditions and potential reversals.

    Where:
        - Use in mean-reversion strategies (e.g., buy when %K crosses above %D in oversold territory).
    """
    low_min = df["low"].rolling(window=period).min()
    high_max = df["high"].rolling(window=period).max()
    k = 100 * ((df["close"] - low_min) / (high_max - low_min))
    d = k.rolling(window=smooth_k).mean()
    return pd.DataFrame({"%K": k, "%D": d})


# # === EXAMPLE USAGE ===
# if __name__ == "__main__":
#     # Load sample data (replace with your own data)
#     data = {
#         "date": pd.date_range(start="2023-01-01", periods=100),
#         "open": np.random.rand(100) * 100,
#         "high": np.random.rand(100) * 100,
#         "low": np.random.rand(100) * 100,
#         "close": np.random.rand(100) * 100,
#         "volume": np.random.randint(100, 1000, size=100)
#     }
#     df = pd.DataFrame(data)

#     # Calculate indicators
#     df["SMA"] = calculate_sma(df, period=14, column="close")
#     df["EMA"] = calculate_ema(df, period=14, column="close")
#     df["RSI"] = calculate_rsi(df, period=14, column="close")
#     macd_df = calculate_macd(df, fast_period=12, slow_period=26, signal_period=9, column="close")
#     bollinger_df = calculate_bollinger_bands(df, period=20, column="close")
#     df["ATR"] = calculate_atr(df, period=14)
#     stochastic_df = calculate_stochastic_oscillator(df, period=14, smooth_k=3, smooth_d=3)

#     # Print results
#     print(df.tail())
#     print(macd_df.tail())
#     print(bollinger_df.tail())
#     print(stochastic_df.tail())
# import pandas as pd
# import numpy as np

# === COMMODITY CHANNEL INDEX (CCI) ===
def calculate_cci(df, period=20):
    """
    Calculate the Commodity Channel Index (CCI).

    Args:
        df (pd.DataFrame): DataFrame containing price data with columns "high", "low", and "close".
        period (int): The period for the CCI calculation.

    Returns:
        pd.Series: A Pandas Series containing the CCI values.

    Hint:
        - CCI measures the difference between the current price and its statistical mean.
        - Values above +100 indicate overbought conditions, and below -100 indicate oversold.

    Why:
        - Helps identify overbought/oversold conditions and potential reversals.

    Where:
        - Use in mean-reversion strategies (e.g., buy when CCI < -100, sell when CCI > +100).
    """
    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    sma = typical_price.rolling(window=period).mean()
    mean_deviation = np.abs(typical_price - sma).rolling(window=period).mean()
    cci = (typical_price - sma) / (0.015 * mean_deviation)
    return cci


# === WILLIAMS %R ===
def calculate_williams_r(df, period=14):
    """
    Calculate Williams %R.

    Args:
        df (pd.DataFrame): DataFrame containing price data with columns "high", "low", and "close".
        period (int): The period for the Williams %R calculation.

    Returns:
        pd.Series: A Pandas Series containing the Williams %R values.

    Hint:
        - Williams %R ranges from -100 to 0. Values above -20 indicate overbought, and below -80 indicate oversold.

    Why:
        - Helps identify overbought/oversold conditions.

    Where:
        - Use in mean-reversion strategies (e.g., buy when %R < -80, sell when %R > -20).
    """
    highest_high = df["high"].rolling(window=period).max()
    lowest_low = df["low"].rolling(window=period).min()
    williams_r = -100 * ((highest_high - df["close"]) / (highest_high - lowest_low))
    return williams_r


# === ON-BALANCE VOLUME (OBV) ===
def calculate_obv(df):
    """
    Calculate On-Balance Volume (OBV).

    Args:
        df (pd.DataFrame): DataFrame containing price data with columns "close" and "volume".

    Returns:
        pd.Series: A Pandas Series containing the OBV values.

    Hint:
        - OBV measures buying and selling pressure by adding volume on up days and subtracting volume on down days.

    Why:
        - Helps confirm price trends and identify divergences.

    Where:
        - Use in trend-confirmation strategies (e.g., buy when OBV confirms an uptrend).
    """
    obv = (np.sign(df["close"].diff()) * df["volume"]).cumsum()
    return obv


# === AROON INDICATOR ===
def calculate_aroon(df, period=14):
    """
    Calculate the Aroon Indicator.

    Args:
        df (pd.DataFrame): DataFrame containing price data with columns "high" and "low".
        period (int): The period for the Aroon calculation.

    Returns:
        pd.DataFrame: A DataFrame containing Aroon Up and Aroon Down.

    Hint:
        - Aroon Up measures the time since the highest high, and Aroon Down measures the time since the lowest low.
        - Values range from 0 to 100. High Aroon Up indicates a strong uptrend, and high Aroon Down indicates a strong downtrend.

    Why:
        - Helps identify trend strength and potential reversals.

    Where:
        - Use in trend-following strategies (e.g., buy when Aroon Up crosses above Aroon Down).
    """
    aroon_up = 100 * (df["high"].rolling(window=period).apply(np.argmax) + 1) / period
    aroon_down = 100 * (df["low"].rolling(window=period).apply(np.argmin) + 1) / period
    return pd.DataFrame({"Aroon Up": aroon_up, "Aroon Down": aroon_down})


# === PARABOLIC SAR ===
def calculate_parabolic_sar(df, acceleration=0.02, maximum=0.2):
    """
    Calculate Parabolic SAR.

    Args:
        df (pd.DataFrame): DataFrame containing price data with columns "high" and "low".
        acceleration (float): The acceleration factor.
        maximum (float): The maximum acceleration factor.

    Returns:
        pd.Series: A Pandas Series containing the Parabolic SAR values.

    Hint:
        - Parabolic SAR is a trend-following indicator that appears as dots above or below the price.

    Why:
        - Helps identify potential reversals and stop-loss levels.

    Where:
        - Use in trend-following strategies (e.g., buy when SAR is below the price, sell when SAR is above the price).
    """
    high = df["high"].values
    low = df["low"].values
    sar = np.zeros(len(df))
    trend = 1  # 1 for uptrend, -1 for downtrend
    ep = high[0]  # Extreme point
    af = acceleration  # Acceleration factor

    for i in range(1, len(df)):
        if trend == 1:
            sar[i] = sar[i - 1] + af * (ep - sar[i - 1])
            if high[i] > ep:
                ep = high[i]
                af = min(af + acceleration, maximum)
            if sar[i] > low[i]:
                trend = -1
                sar[i] = ep
                ep = low[i]
                af = acceleration
        else:
            sar[i] = sar[i - 1] + af * (ep - sar[i - 1])
            if low[i] < ep:
                ep = low[i]
                af = min(af + acceleration, maximum)
            if sar[i] < high[i]:
                trend = 1
                sar[i] = ep
                ep = high[i]
                af = acceleration
    return pd.Series(sar, index=df.index)


# === ICHIMOKU CLOUD ===
def calculate_ichimoku_cloud(df, conversion_period=9, base_period=26, lagging_period=52, displacement=26):
    """
    Calculate Ichimoku Cloud.

    Args:
        df (pd.DataFrame): DataFrame containing price data with columns "high" and "low".
        conversion_period (int): The period for the Tenkan-sen (Conversion Line).
        base_period (int): The period for the Kijun-sen (Base Line).
        lagging_period (int): The period for the Chikou Span (Lagging Line).
        displacement (int): The displacement for the Senkou Span (Leading Span).

    Returns:
        pd.DataFrame: A DataFrame containing all Ichimoku components.

    Hint:
        - Ichimoku Cloud provides support/resistance levels, trend direction, and momentum.

    Why:
        - Offers a comprehensive view of the market in one indicator.

    Where:
        - Use in trend-following strategies (e.g., buy when price is above the cloud).
    """
    tenkan_sen = (df["high"].rolling(window=conversion_period).max() + df["low"].rolling(window=conversion_period).min()) / 2
    kijun_sen = (df["high"].rolling(window=base_period).max() + df["low"].rolling(window=base_period).min()) / 2
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(displacement)
    senkou_span_b = ((df["high"].rolling(window=lagging_period).max() + df["low"].rolling(window=lagging_period).min()) / 2).shift(displacement)
    chikou_span = df["close"].shift(-displacement)
    return pd.DataFrame({
        "Tenkan Sen": tenkan_sen,
        "Kijun Sen": kijun_sen,
        "Senkou Span A": senkou_span_a,
        "Senkou Span B": senkou_span_b,
        "Chikou Span": chikou_span
    })


# # === EXAMPLE USAGE ===
# if __name__ == "__main__":
#     # Load sample data (replace with your own data)
#     data = {
#         "date": pd.date_range(start="2023-01-01", periods=100),
#         "open": np.random.rand(100) * 100,
#         "high": np.random.rand(100) * 100,
#         "low": np.random.rand(100) * 100,
#         "close": np.random.rand(100) * 100,
#         "volume": np.random.randint(100, 1000, size=100)
#     }
#     df = pd.DataFrame(data)

#     # Calculate indicators
#     df["CCI"] = calculate_cci(df, period=20)
#     df["Williams %R"] = calculate_williams_r(df, period=14)
#     df["OBV"] = calculate_obv(df)
#     aroon_df = calculate_aroon(df, period=14)
#     df["Parabolic SAR"] = calculate_parabolic_sar(df)
#     ichimoku_df = calculate_ichimoku_cloud(df)

#     # Print results
#     print(df.tail())
#     print(aroon_df.tail())
#     print(ichimoku_df.tail())
import pandas as pd
import numpy as np

# === MONEY FLOW INDEX (MFI) ===
def calculate_mfi(df, period=14):
    """
    Calculate the Money Flow Index (MFI).

    Args:
        df (pd.DataFrame): DataFrame containing price data with columns "high", "low", "close", and "volume".
        period (int): The period for the MFI calculation.

    Returns:
        pd.Series: A Pandas Series containing the MFI values.

    Hint:
        - MFI ranges from 0 to 100. Values above 80 indicate overbought conditions, and below 20 indicate oversold.

    Why:
        - Combines price and volume to measure buying and selling pressure.

    Where:
        - Use in mean-reversion strategies (e.g., buy when MFI < 20, sell when MFI > 80).
    """
    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    money_flow = typical_price * df["volume"]
    positive_flow = (typical_price.diff() > 0) * money_flow
    negative_flow = (typical_price.diff() < 0) * money_flow
    money_ratio = positive_flow.rolling(window=period).sum() / negative_flow.rolling(window=period).sum()
    mfi = 100 - (100 / (1 + money_ratio))
    return mfi


# === STANDARD DEVIATION ===
def calculate_std(df, period=20, column="close"):
    """
    Calculate Standard Deviation.

    Args:
        df (pd.DataFrame): DataFrame containing price data.
        period (int): The period for the standard deviation calculation.
        column (str): The column name for the price data (default is "close").

    Returns:
        pd.Series: A Pandas Series containing the standard deviation values.

    Hint:
        - Measures the volatility of price movements.

    Why:
        - Helps assess market volatility and set stop-loss levels.

    Where:
        - Use in volatility-based strategies or to adjust position sizing.
    """
    return df[column].rolling(window=period).std()


# === CHAIKIN VOLATILITY ===
def calculate_chaikin_volatility(df, period=10, ema_period=10):
    """
    Calculate Chaikin Volatility.

    Args:
        df (pd.DataFrame): DataFrame containing price data with columns "high" and "low".
        period (int): The period for the volatility calculation.
        ema_period (int): The period for the EMA smoothing.

    Returns:
        pd.Series: A Pandas Series containing the Chaikin Volatility values.

    Hint:
        - Measures the rate of change of the trading range (high - low).

    Why:
        - Helps identify periods of high or low volatility.

    Where:
        - Use in volatility-based strategies (e.g., buy during low volatility, sell during high volatility).
    """
    ema = calculate_ema(df, period=ema_period, column="close")
    volatility = ((df["high"] - df["low"]).rolling(window=period).mean() / ema) * 100
    return volatility


# === RATE OF CHANGE (ROC) ===
def calculate_roc(df, period=14, column="close"):
    """
    Calculate Rate of Change (ROC).

    Args:
        df (pd.DataFrame): DataFrame containing price data.
        period (int): The period for the ROC calculation.
        column (str): The column name for the price data (default is "close").

    Returns:
        pd.Series: A Pandas Series containing the ROC values.

    Hint:
        - Measures the percentage change in price over a specified period.

    Why:
        - Helps identify momentum and potential reversals.

    Where:
        - Use in momentum-based strategies (e.g., buy when ROC crosses above zero).
    """
    return df[column].pct_change(periods=period) * 100


# === AVERAGE DIRECTIONAL INDEX (ADX) ===
def calculate_adx(df, period=14):
    """
    Calculate the Average Directional Index (ADX).

    Args:
        df (pd.DataFrame): DataFrame containing price data with columns "high", "low", and "close".
        period (int): The period for the ADX calculation.

    Returns:
        pd.DataFrame: A DataFrame containing ADX, +DI, and -DI.

    Hint:
        - ADX measures trend strength, while +DI and -DI measure trend direction.

    Why:
        - Helps identify strong trends and their direction.

    Where:
        - Use in trend-following strategies (e.g., buy when ADX > 25 and +DI > -DI).
    """
    up = df["high"].diff()
    down = -df["low"].diff()
    plus_dm = np.where((up > down) & (up > 0), up, 0)
    minus_dm = np.where((down > up) & (down > 0), down, 0)
    tr = np.maximum(df["high"] - df["low"], np.maximum(np.abs(df["high"] - df["close"].shift()), np.abs(df["low"] - df["close"].shift())))
    atr = tr.rolling(window=period).mean()
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(window=period).mean()
    return pd.DataFrame({"ADX": adx, "+DI": plus_di, "-DI": minus_di})


# === KELTNER CHANNELS ===
def calculate_keltner_channels(df, period=20, multiplier=2, atr_period=10):
    """
    Calculate Keltner Channels.

    Args:
        df (pd.DataFrame): DataFrame containing price data with columns "high", "low", and "close".
        period (int): The period for the EMA calculation.
        multiplier (float): The multiplier for the ATR.
        atr_period (int): The period for the ATR calculation.

    Returns:
        pd.DataFrame: A DataFrame containing Upper Band, Middle Band (EMA), and Lower Band.

    Hint:
        - Keltner Channels are volatility-based bands around an EMA.

    Why:
        - Helps identify overbought/oversold conditions and potential breakouts.

    Where:
        - Use in volatility-based strategies (e.g., buy when price touches the lower band, sell when it touches the upper band).
    """
    ema = calculate_ema(df, period=period, column="close")
    atr = calculate_atr(df, period=atr_period)
    upper_band = ema + (multiplier * atr)
    lower_band = ema - (multiplier * atr)
    return pd.DataFrame({"Upper Band": upper_band, "Middle Band": ema, "Lower Band": lower_band})


# # === EXAMPLE USAGE ===
# if __name__ == "__main__":
#     # Load sample data (replace with your own data)
#     data = {
#         "date": pd.date_range(start="2023-01-01", periods=100),
#         "open": np.random.rand(100) * 100,
#         "high": np.random.rand(100) * 100,
#         "low": np.random.rand(100) * 100,
#         "close": np.random.rand(100) * 100,
#         "volume": np.random.randint(100, 1000, size=100)
#     }
#     df = pd.DataFrame(data)

#     # Calculate indicators
#     df["MFI"] = calculate_mfi(df, period=14)
#     df["STD"] = calculate_std(df, period=20, column="close")
#     df["Chaikin Volatility"] = calculate_chaikin_volatility(df, period=10, ema_period=10)
#     df["ROC"] = calculate_roc(df, period=14, column="close")
#     adx_df = calculate_adx(df, period=14)
#     keltner_df = calculate_keltner_channels(df, period=20, multiplier=2, atr_period=10)

#     # Print results
#     print(df.tail())
#     print(adx_df.tail())
#     print(keltner_df.tail())