# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Currency conversion tool for Mekong Voyager."""

import json
import urllib.request
from typing import Any

EXCHANGE_API_URL = "https://open.er-api.com/v6/latest/USD"


def convert_currency(
    amount: float,
    from_currency: str = "USD",
    to_currency: str = "VND",
) -> dict[str, Any]:
    """Convert a monetary amount from one currency to another using live exchange rates.

    Args:
        amount: The monetary amount to convert (e.g. 100.0).
        from_currency: 3-letter currency code to convert from (e.g. 'USD', 'EUR', 'SGD').
        to_currency: 3-letter currency code to convert to (e.g. 'VND', 'THB', 'KHR', 'LAK').

    Returns:
        A dictionary containing the conversion results and live exchange rate.
    """
    from_curr = from_currency.upper().strip()
    to_curr = to_currency.upper().strip()

    try:
        req = urllib.request.Request(
            EXCHANGE_API_URL,
            headers={"User-Agent": "MekongVoyager/1.0"},
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        rates = data.get("rates", {})
        if from_curr not in rates or to_curr not in rates:
            return {
                "error": f"Unsupported currency code '{from_curr}' or '{to_curr}'. Supported examples: USD, VND, THB, KHR, LAK, SGD, EUR."
            }

        usd_amount = amount / rates[from_curr]
        converted = usd_amount * rates[to_curr]
        rate = rates[to_curr] / rates[from_curr]

        return {
            "status": "success",
            "amount": amount,
            "from_currency": from_curr,
            "to_currency": to_curr,
            "converted_amount": round(converted, 2),
            "exchange_rate": round(rate, 4),
            "formatted_result": f"{amount:,.2f} {from_curr} = {converted:,.2f} {to_curr}",
        }
    except Exception as exc:
        # Fallback estimation if network call fails
        fallback_rates = {
            "USD": 1.0,
            "VND": 25900.0,
            "THB": 33.5,
            "KHR": 4100.0,
            "LAK": 22000.0,
            "EUR": 0.92,
            "SGD": 1.35,
        }
        if from_curr in fallback_rates and to_curr in fallback_rates:
            converted = (amount / fallback_rates[from_curr]) * fallback_rates[to_curr]
            return {
                "status": "success (estimated)",
                "amount": amount,
                "from_currency": from_curr,
                "to_currency": to_curr,
                "converted_amount": round(converted, 2),
                "formatted_result": f"{amount:,.2f} {from_curr} ≈ {converted:,.2f} {to_curr} (Estimated)",
            }
        return {"error": f"Failed to fetch exchange rate: {str(exc)}"}
