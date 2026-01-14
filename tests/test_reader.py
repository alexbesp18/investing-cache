"""Tests for investing-cache package."""

import os
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from investing_cache import TickerCache, TickerData, TickerCacheError, TickerNotFoundError


class TestTickerData:
    """Tests for TickerData model."""

    def test_from_dict(self):
        """Test creating TickerData from a dictionary."""
        data = {
            "symbol": "AAPL",
            "date": "2025-01-13",
            "close": 150.25,
            "rsi": 45.5,
            "bullish_score": 7.5,
        }

        ticker = TickerData.from_dict(data)

        assert ticker.symbol == "AAPL"
        assert ticker.date == date(2025, 1, 13)
        assert ticker.close == 150.25
        assert ticker.rsi == 45.5
        assert ticker.bullish_score == 7.5

    def test_from_dict_with_none_values(self):
        """Test handling None/missing values."""
        data = {
            "symbol": "AAPL",
            "date": "2025-01-13",
            "close": None,
            "rsi": None,
        }

        ticker = TickerData.from_dict(data)

        assert ticker.symbol == "AAPL"
        assert ticker.close is None
        assert ticker.rsi is None

    def test_to_dict(self):
        """Test converting TickerData to dictionary."""
        ticker = TickerData(
            symbol="AAPL",
            date=date(2025, 1, 13),
            close=150.25,
            rsi=45.5,
        )

        result = ticker.to_dict()

        assert result["symbol"] == "AAPL"
        assert result["date"] == "2025-01-13"
        assert result["close"] == 150.25
        assert result["rsi"] == 45.5
        # None values should be excluded
        assert "macd" not in result

    def test_frozen_dataclass(self):
        """Test that TickerData is immutable."""
        ticker = TickerData(symbol="AAPL", date=date(2025, 1, 13))

        with pytest.raises(AttributeError):
            ticker.symbol = "GOOGL"


class TestTickerCache:
    """Tests for TickerCache."""

    def test_not_configured(self):
        """Test behavior when not configured."""
        with patch.dict(os.environ, {}, clear=True):
            cache = TickerCache()
            assert not cache.is_configured

    def test_configured_from_env(self):
        """Test configuration from environment variables."""
        with patch.dict(
            os.environ,
            {
                "SUPABASE_URL": "https://test.supabase.co",
                "SUPABASE_ANON_KEY": "test-key",
            },
        ):
            cache = TickerCache()
            assert cache.is_configured
            assert cache.url == "https://test.supabase.co"
            assert cache.key == "test-key"

    def test_configured_from_params(self):
        """Test configuration from constructor params."""
        cache = TickerCache(
            url="https://custom.supabase.co",
            key="custom-key",
        )
        assert cache.is_configured
        assert cache.url == "https://custom.supabase.co"

    def test_repr(self):
        """Test string representation."""
        with patch.dict(os.environ, {}, clear=True):
            cache = TickerCache()
            assert "not configured" in repr(cache)

        cache2 = TickerCache(url="https://test.supabase.co", key="key")
        assert "configured" in repr(cache2)

    def test_client_access_not_configured(self):
        """Test that accessing client raises error when not configured."""
        with patch.dict(os.environ, {}, clear=True):
            cache = TickerCache()
            with pytest.raises(TickerCacheError) as exc_info:
                _ = cache.client
            assert "not configured" in str(exc_info.value)


# Integration tests (require real Supabase connection)
@pytest.mark.skipif(
    not os.environ.get("SUPABASE_URL"),
    reason="Integration tests require SUPABASE_URL env var",
)
class TestIntegration:
    """Integration tests with real Supabase connection."""

    def test_get_real_ticker(self):
        """Test fetching a real ticker from Supabase."""
        cache = TickerCache()
        data = cache.get("AAPL")

        assert data.symbol == "AAPL"
        assert data.date is not None
        assert data.close is not None or data.rsi is not None

    def test_list_real_tickers(self):
        """Test listing real tickers from Supabase."""
        cache = TickerCache()
        tickers = cache.list_tickers()

        assert len(tickers) > 0
        assert all(isinstance(t, str) for t in tickers)
