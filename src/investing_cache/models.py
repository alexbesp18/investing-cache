"""Data models for investing-cache."""

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class TickerData:
    """
    Daily indicator data for a single ticker.

    Contains technical indicators, scores, and metadata from the
    daily_indicators table in Supabase.
    """

    # Identity
    symbol: str
    date: date

    # Price
    close: Optional[float] = None

    # Momentum indicators
    rsi: Optional[float] = None
    stoch_k: Optional[float] = None
    stoch_d: Optional[float] = None
    williams_r: Optional[float] = None
    roc: Optional[float] = None

    # Trend indicators
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    adx: Optional[float] = None

    # Moving averages
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None

    # Volatility
    bb_upper: Optional[float] = None
    bb_lower: Optional[float] = None
    bb_position: Optional[float] = None
    atr: Optional[float] = None

    # Volume
    volume: Optional[int] = None
    volume_ratio: Optional[float] = None
    obv: Optional[int] = None

    # Scores (0-10 scale)
    bullish_score: Optional[float] = None
    reversal_score: Optional[float] = None
    oversold_score: Optional[float] = None

    # Score component breakdowns (JSONB)
    bullish_components: Optional[Dict[str, Any]] = None
    reversal_components: Optional[Dict[str, Any]] = None
    oversold_components: Optional[Dict[str, Any]] = None

    # Reversal details
    reversal_conviction: Optional[str] = None  # HIGH/MEDIUM/LOW/NONE
    reversal_raw_score: Optional[float] = None
    reversal_volume_multiplier: Optional[float] = None
    reversal_adx_multiplier: Optional[float] = None

    # Divergence
    divergence_type: Optional[str] = None  # none/bullish/bearish
    divergence_strength: Optional[float] = None

    # 52-week context
    price_52w_high: Optional[float] = None
    pct_from_52w_high: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TickerData":
        """
        Create TickerData from a Supabase row dictionary.

        Args:
            data: Row from daily_indicators table

        Returns:
            TickerData instance
        """
        # Parse date string to date object
        date_val = data.get("date")
        if isinstance(date_val, str):
            date_val = date.fromisoformat(date_val)

        return cls(
            symbol=data.get("symbol", ""),
            date=date_val,
            close=data.get("close"),
            # Momentum
            rsi=data.get("rsi"),
            stoch_k=data.get("stoch_k"),
            stoch_d=data.get("stoch_d"),
            williams_r=data.get("williams_r"),
            roc=data.get("roc"),
            # Trend
            macd=data.get("macd"),
            macd_signal=data.get("macd_signal"),
            macd_hist=data.get("macd_hist"),
            adx=data.get("adx"),
            # Moving averages
            sma_20=data.get("sma_20"),
            sma_50=data.get("sma_50"),
            sma_200=data.get("sma_200"),
            # Volatility
            bb_upper=data.get("bb_upper"),
            bb_lower=data.get("bb_lower"),
            bb_position=data.get("bb_position"),
            atr=data.get("atr"),
            # Volume
            volume=data.get("volume"),
            volume_ratio=data.get("volume_ratio"),
            obv=data.get("obv"),
            # Scores
            bullish_score=data.get("bullish_score"),
            reversal_score=data.get("reversal_score"),
            oversold_score=data.get("oversold_score"),
            # Components
            bullish_components=data.get("bullish_components"),
            reversal_components=data.get("reversal_components"),
            oversold_components=data.get("oversold_components"),
            # Reversal details
            reversal_conviction=data.get("reversal_conviction"),
            reversal_raw_score=data.get("reversal_raw_score"),
            reversal_volume_multiplier=data.get("reversal_volume_multiplier"),
            reversal_adx_multiplier=data.get("reversal_adx_multiplier"),
            # Divergence
            divergence_type=data.get("divergence_type"),
            divergence_strength=data.get("divergence_strength"),
            # 52-week
            price_52w_high=data.get("price_52w_high"),
            pct_from_52w_high=data.get("pct_from_52w_high"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excludes None values)."""
        result = {
            "symbol": self.symbol,
            "date": self.date.isoformat() if self.date else None,
        }

        # Add non-None fields
        fields = [
            "close",
            "rsi",
            "stoch_k",
            "stoch_d",
            "williams_r",
            "roc",
            "macd",
            "macd_signal",
            "macd_hist",
            "adx",
            "sma_20",
            "sma_50",
            "sma_200",
            "bb_upper",
            "bb_lower",
            "bb_position",
            "atr",
            "volume",
            "volume_ratio",
            "obv",
            "bullish_score",
            "reversal_score",
            "oversold_score",
            "bullish_components",
            "reversal_components",
            "oversold_components",
            "reversal_conviction",
            "reversal_raw_score",
            "reversal_volume_multiplier",
            "reversal_adx_multiplier",
            "divergence_type",
            "divergence_strength",
            "price_52w_high",
            "pct_from_52w_high",
        ]

        for field in fields:
            value = getattr(self, field)
            if value is not None:
                result[field] = value

        return result
