# investing-cache

Read-only access to daily stock indicators from Supabase.

This package provides a simple interface to read technical indicators and scores that are populated by a separate daily workflow. It's designed to be used from any Python project without dependencies on the data-producing codebase.

## Installation

```bash
# From GitHub
pip install git+https://github.com/alexbespalov/investing-cache.git

# Local development
pip install -e /path/to/investing-cache
```

## Setup

Set the following environment variables:

```bash
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_ANON_KEY=your-anon-key
```

## Usage

### Basic Usage

```python
from investing_cache import TickerCache

# Initialize (reads env vars automatically)
cache = TickerCache()

# Get data for a single ticker
data = cache.get("AAPL")
print(f"Symbol: {data.symbol}")
print(f"Date: {data.date}")
print(f"Close: ${data.close:.2f}")
print(f"RSI: {data.rsi:.1f}")
print(f"Bullish Score: {data.bullish_score}")
```

### Batch Queries

```python
# Get multiple tickers at once
batch = cache.get_batch(["AAPL", "GOOGL", "MSFT", "NVDA"])
for symbol, data in batch.items():
    print(f"{symbol}: RSI={data.rsi:.1f}, Score={data.bullish_score}")
```

### List Available Tickers

```python
# Get all tickers from the latest date
tickers = cache.list_tickers()
print(f"Found {len(tickers)} tickers")
```

### Get Top Scores

```python
# Get tickers with highest bullish scores
top_bullish = cache.get_top_scores(
    score_type="bullish_score",
    min_score=7.0,
    limit=10
)
for data in top_bullish:
    print(f"{data.symbol}: {data.bullish_score}")

# Get tickers with highest reversal scores
top_reversals = cache.get_top_scores(
    score_type="reversal_score",
    min_score=6.0,
    limit=10
)
```

### Historical Data

```python
# Get last 30 days of data for a ticker
history = cache.get_history("AAPL", days=30)
for data in history:
    print(f"{data.date}: RSI={data.rsi:.1f}")
```

### Specific Date

```python
from datetime import date

# Get data for a specific date
data = cache.get("AAPL", target_date=date(2025, 1, 10))
```

## Available Fields

The `TickerData` object contains all fields from the daily_indicators table:

### Price & Identity
- `symbol`: Stock ticker
- `date`: Data date
- `close`: Closing price

### Momentum Indicators
- `rsi`: Relative Strength Index (0-100)
- `stoch_k`: Stochastic %K
- `stoch_d`: Stochastic %D
- `williams_r`: Williams %R (-100 to 0)
- `roc`: Rate of Change

### Trend Indicators
- `macd`: MACD line
- `macd_signal`: MACD signal line
- `macd_hist`: MACD histogram
- `adx`: Average Directional Index

### Moving Averages
- `sma_20`: 20-day SMA
- `sma_50`: 50-day SMA
- `sma_200`: 200-day SMA

### Volatility
- `bb_upper`: Bollinger Band upper
- `bb_lower`: Bollinger Band lower
- `bb_position`: Position within bands (0-1)
- `atr`: Average True Range

### Volume
- `volume`: Trading volume
- `volume_ratio`: Volume vs average
- `obv`: On-Balance Volume

### Scores (0-10 scale)
- `bullish_score`: Overall bullish rating
- `reversal_score`: Reversal potential
- `oversold_score`: Oversold level

### Score Components (JSONB)
- `bullish_components`: Breakdown of bullish score
- `reversal_components`: Breakdown of reversal score
- `oversold_components`: Breakdown of oversold score

### Additional Fields
- `divergence_type`: "bullish", "bearish", or "none"
- `divergence_strength`: Strength of divergence (0-10)
- `price_52w_high`: 52-week high price
- `pct_from_52w_high`: Percentage below 52-week high

## Error Handling

```python
from investing_cache import TickerCache, TickerNotFoundError, TickerCacheError

cache = TickerCache()

try:
    data = cache.get("INVALID")
except TickerNotFoundError:
    print("Ticker not found")
except TickerCacheError as e:
    print(f"Database error: {e}")
```

## License

MIT
