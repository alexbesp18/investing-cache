"""
investing-cache: Read-only access to daily stock indicators from Supabase.

This package provides a simple interface to read technical indicators
and scores from the daily_indicators table in Supabase. The data is
populated by a separate daily workflow and this package only reads.

Usage:
    from investing_cache import TickerCache, TickerData

    cache = TickerCache()
    data = cache.get("AAPL")
    print(f"RSI: {data.rsi}, Bullish Score: {data.bullish_score}")

Environment Variables:
    SUPABASE_URL: Your Supabase project URL
    SUPABASE_ANON_KEY: Your Supabase anon key (read-only access)
"""

from .models import TickerData
from .reader import TickerCache, TickerCacheError, TickerNotFoundError

__version__ = "0.1.0"
__all__ = [
    "TickerCache",
    "TickerData",
    "TickerCacheError",
    "TickerNotFoundError",
]
