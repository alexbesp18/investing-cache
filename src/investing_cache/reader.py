"""
TickerCache - Read-only access to daily stock indicators from Supabase.

Reads from the investing_one.daily_indicators table which is populated
by the 007-ticker-analysis daily workflow.
"""

import logging
import os
from datetime import date
from typing import Dict, List, Optional

from .models import TickerData

logger = logging.getLogger(__name__)


class TickerCacheError(Exception):
    """Base exception for TickerCache errors."""

    pass


class TickerNotFoundError(TickerCacheError):
    """Raised when a ticker is not found in the cache."""

    pass


class TickerCache:
    """
    Read-only cache for daily stock indicators.

    Connects to Supabase and reads from the investing_one.daily_indicators
    table. All data is read-only - this package never writes to the database.

    Usage:
        cache = TickerCache()
        data = cache.get("AAPL")
        print(f"RSI: {data.rsi}, Score: {data.bullish_score}")

    Environment variables:
        SUPABASE_URL: Supabase project URL
        SUPABASE_ANON_KEY: Supabase anon key (read-only access)
    """

    def __init__(
        self,
        url: Optional[str] = None,
        key: Optional[str] = None,
        schema: str = "investing_one",
        table: str = "daily_indicators",
    ):
        """
        Initialize the ticker cache.

        Args:
            url: Supabase URL (defaults to SUPABASE_URL env var)
            key: Supabase anon key (defaults to SUPABASE_ANON_KEY env var)
            schema: Database schema (default: investing_one)
            table: Table name (default: daily_indicators)
        """
        self.url = url or os.environ.get("SUPABASE_URL")
        self.key = key or os.environ.get("SUPABASE_ANON_KEY")
        self.schema = schema
        self.table = table
        self._client = None
        self._latest_date: Optional[date] = None

        if not self.url or not self.key:
            logger.warning(
                "Supabase credentials not configured. "
                "Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
            )

    @property
    def client(self):
        """Lazy-load the Supabase client."""
        if self._client is None:
            if not self.url or not self.key:
                raise TickerCacheError(
                    "Supabase credentials not configured. "
                    "Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
                )
            try:
                from supabase import create_client

                self._client = create_client(self.url, self.key)
            except ImportError:
                raise TickerCacheError(
                    "supabase package not installed. Run: pip install supabase"
                )
        return self._client

    @property
    def is_configured(self) -> bool:
        """Check if Supabase credentials are available."""
        return bool(self.url and self.key)

    def _get_latest_date(self) -> date:
        """Get the most recent date in the database (cached)."""
        if self._latest_date is None:
            result = (
                self.client.schema(self.schema)
                .table(self.table)
                .select("date")
                .order("date", desc=True)
                .limit(1)
                .execute()
            )

            if not result.data:
                raise TickerCacheError("No data found in daily_indicators table")

            date_str = result.data[0]["date"]
            self._latest_date = (
                date.fromisoformat(date_str) if isinstance(date_str, str) else date_str
            )

        return self._latest_date

    def get(
        self,
        symbol: str,
        target_date: Optional[date] = None,
    ) -> TickerData:
        """
        Get indicator data for a single ticker.

        Args:
            symbol: Stock ticker symbol (e.g., "AAPL")
            target_date: Specific date to fetch (defaults to latest)

        Returns:
            TickerData with all available indicators

        Raises:
            TickerNotFoundError: If ticker not found for the date
            TickerCacheError: If database connection fails
        """
        symbol = symbol.upper()
        query_date = target_date or self._get_latest_date()

        try:
            result = (
                self.client.schema(self.schema)
                .table(self.table)
                .select("*")
                .eq("symbol", symbol)
                .eq("date", query_date.isoformat())
                .execute()
            )

            if not result.data:
                raise TickerNotFoundError(
                    f"Ticker {symbol} not found for date {query_date}"
                )

            return TickerData.from_dict(result.data[0])

        except TickerNotFoundError:
            raise
        except Exception as e:
            raise TickerCacheError(f"Failed to fetch {symbol}: {e}")

    def get_batch(
        self,
        symbols: List[str],
        target_date: Optional[date] = None,
    ) -> Dict[str, TickerData]:
        """
        Get indicator data for multiple tickers.

        Args:
            symbols: List of ticker symbols
            target_date: Specific date to fetch (defaults to latest)

        Returns:
            Dict mapping symbol -> TickerData (missing tickers are excluded)
        """
        if not symbols:
            return {}

        symbols = [s.upper() for s in symbols]
        query_date = target_date or self._get_latest_date()

        try:
            result = (
                self.client.schema(self.schema)
                .table(self.table)
                .select("*")
                .in_("symbol", symbols)
                .eq("date", query_date.isoformat())
                .execute()
            )

            return {row["symbol"]: TickerData.from_dict(row) for row in result.data}

        except Exception as e:
            raise TickerCacheError(f"Failed to fetch batch: {e}")

    def list_tickers(self, target_date: Optional[date] = None) -> List[str]:
        """
        List all tickers available for a date.

        Args:
            target_date: Specific date (defaults to latest)

        Returns:
            Sorted list of ticker symbols
        """
        query_date = target_date or self._get_latest_date()

        try:
            result = (
                self.client.schema(self.schema)
                .table(self.table)
                .select("symbol")
                .eq("date", query_date.isoformat())
                .order("symbol")
                .execute()
            )

            return [row["symbol"] for row in result.data]

        except Exception as e:
            raise TickerCacheError(f"Failed to list tickers: {e}")

    def get_latest_date(self) -> date:
        """Get the most recent date with data."""
        return self._get_latest_date()

    def get_history(
        self,
        symbol: str,
        days: int = 30,
    ) -> List[TickerData]:
        """
        Get historical indicator data for a ticker.

        Args:
            symbol: Stock ticker symbol
            days: Number of days of history

        Returns:
            List of TickerData ordered by date (most recent first)
        """
        symbol = symbol.upper()

        try:
            result = (
                self.client.schema(self.schema)
                .table(self.table)
                .select("*")
                .eq("symbol", symbol)
                .order("date", desc=True)
                .limit(days)
                .execute()
            )

            return [TickerData.from_dict(row) for row in result.data]

        except Exception as e:
            raise TickerCacheError(f"Failed to fetch history for {symbol}: {e}")

    def get_top_scores(
        self,
        score_type: str = "bullish_score",
        min_score: float = 7.0,
        limit: int = 20,
        target_date: Optional[date] = None,
    ) -> List[TickerData]:
        """
        Get tickers with highest scores.

        Args:
            score_type: Score column (bullish_score, reversal_score, oversold_score)
            min_score: Minimum score threshold
            limit: Maximum results
            target_date: Specific date (defaults to latest)

        Returns:
            List of TickerData sorted by score (highest first)
        """
        query_date = target_date or self._get_latest_date()

        try:
            result = (
                self.client.schema(self.schema)
                .table(self.table)
                .select("*")
                .eq("date", query_date.isoformat())
                .gte(score_type, min_score)
                .order(score_type, desc=True)
                .limit(limit)
                .execute()
            )

            return [TickerData.from_dict(row) for row in result.data]

        except Exception as e:
            raise TickerCacheError(f"Failed to fetch top scores: {e}")

    def __repr__(self) -> str:
        status = "configured" if self.is_configured else "not configured"
        return f"TickerCache({status})"
