# CLAUDE.md

## What This Is

Read-only Python package to access daily stock indicators from Supabase.

**GitHub:** https://github.com/alexbesp18/investing-cache

## How It Works

```
007-ticker-analysis (runs daily in alex-bespalov-portfolio)
        ↓ writes to Supabase daily_indicators table

investing-cache (THIS PACKAGE)
        ↓ reads from Supabase

Any project on any computer can use the data
```

## Commands

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Type check
mypy src/

# Lint
ruff check .
```

## Usage in Other Projects

### Installation
```bash
pip install git+https://github.com/alexbesp18/investing-cache.git
```

### Environment Variables
```bash
export SUPABASE_URL=https://rxsmmrmahnvaarwsngtb.supabase.co
export SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ4c21tcm1haG52YWFyd3NuZ3RiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY4NjE1ODUsImV4cCI6MjA4MjQzNzU4NX0.g_I-w8gJbcrdQOf0mdBl9AduhKTWQJfQ9iIvfsCfG5o
```

### Code
```python
from investing_cache import TickerCache

cache = TickerCache()
data = cache.get("AAPL")
print(f"RSI: {data.rsi}, Oversold: {data.oversold_score}")

# List all ~260 tickers
tickers = cache.list_tickers()

# Batch fetch
batch = cache.get_batch(["AAPL", "NVDA", "MSFT"])

# Historical data
history = cache.get_history("AAPL", days=30)

# Top scores
top = cache.get_top_scores(score_type="oversold_score", min_score=5.0)
```

## Available Data Fields

| Category | Fields |
|----------|--------|
| Price | `close` |
| Momentum | `rsi`, `stoch_k`, `stoch_d`, `williams_r`, `roc` |
| Trend | `macd`, `macd_signal`, `macd_hist`, `adx` |
| Moving Averages | `sma_20`, `sma_50`, `sma_200` |
| Volatility | `bb_upper`, `bb_lower`, `bb_position`, `atr` |
| Volume | `volume`, `volume_ratio`, `obv` |
| Scores | `bullish_score`, `reversal_score`, `oversold_score` |
| AI Commentary | `ai_bullish_reason`, `ai_tech_summary` |

## Data Source

Data comes from `investing_one.daily_indicators` table in Supabase project `rxsmmrmahnvaarwsngtb`.

Updated daily by `007-ticker-analysis` workflow in `alex-bespalov-portfolio` repo.
