from __future__ import annotations

import csv
from datetime import date, datetime
from io import StringIO
from typing import Iterable
from urllib.error import URLError
from urllib.request import urlopen

from ..models import PricePoint


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def load_prices_from_rows(rows: Iterable[dict[str, str]]) -> list[PricePoint]:
    data: list[PricePoint] = []
    for row in rows:
        day = row.get("date") or row.get("Date")
        price = row.get("price") or row.get("Close")
        if not day or not price:
            continue
        data.append(PricePoint(day=parse_date(day), price=float(price)))

    if not data:
        raise ValueError("No valid price rows found")

    data.sort(key=lambda value: value.day)
    return data


def fetch_stooq_prices(symbol: str) -> list[PricePoint]:
    """Fetch daily historical prices from Stooq CSV endpoint."""
    url = f"https://stooq.com/q/d/l/?s={symbol.lower()}&i=d"
    try:
        with urlopen(url, timeout=30) as response:
            payload = response.read().decode("utf-8")
    except URLError as exc:
        raise RuntimeError(f"Could not fetch data from Stooq for '{symbol}': {exc}") from exc

    reader = csv.DictReader(StringIO(payload))
    prices = load_prices_from_rows(reader)
    if len(prices) < 2:
        raise RuntimeError(f"Insufficient data returned by Stooq for '{symbol}'")
    return prices
