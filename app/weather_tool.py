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

"""Live real-time weather tool using the free Open-Meteo public API."""

import json
import os
import urllib.parse
import urllib.request
from typing import Any

# Open-Meteo WMO Weather interpretation codes
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
}


def get_live_weather(location: str) -> dict[str, Any]:
    """Fetch real-time live weather data for any travel destination or city using the Open-Meteo public API.

    Args:
        location: City or destination name (e.g. 'Hanoi', 'Hoi An', 'Siem Reap', 'Bangkok', 'San Francisco').

    Returns:
        A dictionary containing live temperature (°C and °F), weather conditions, wind speed, and location details.
    """
    api_key = os.getenv("WEATHER_API_KEY", "")

    try:
        # Step 1: Geocode location to lat/lon via Open-Meteo free public Geocoding API
        geo_url = (
            f"https://geocoding-api.open-meteo.com/v1/search?"
            f"name={urllib.parse.quote(location.strip())}&count=1&language=en&format=json"
        )
        if api_key:
            geo_url += f"&apikey={api_key}"

        req_geo = urllib.request.Request(
            geo_url,
            headers={"User-Agent": "MekongVoyager/1.0"},
        )
        with urllib.request.urlopen(req_geo, timeout=5) as resp_geo:
            geo_data = json.loads(resp_geo.read().decode("utf-8"))

        results = geo_data.get("results", [])
        if not results:
            return {"error": f"Location '{location}' not found."}

        place = results[0]
        name = place.get("name", location)
        country = place.get("country", "")
        lat, lon = place["latitude"], place["longitude"]

        # Step 2: Fetch current live weather
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current_weather=true"
        )
        req_w = urllib.request.Request(
            weather_url,
            headers={"User-Agent": "MekongVoyager/1.0"},
        )
        with urllib.request.urlopen(req_w, timeout=5) as resp_w:
            weather_data = json.loads(resp_w.read().decode("utf-8"))

        cw = weather_data.get("current_weather", {})
        temp_c = cw.get("temperature", 0.0)
        temp_f = round((temp_c * 9 / 5) + 32, 1)
        code = cw.get("weathercode", 0)
        condition = WEATHER_CODES.get(code, "Clear")
        wind_speed = cw.get("windspeed", 0.0)

        return {
            "status": "success",
            "location": f"{name}, {country}".strip(", "),
            "temperature_celsius": temp_c,
            "temperature_fahrenheit": temp_f,
            "condition": condition,
            "wind_speed_kmh": wind_speed,
            "coordinates": {"latitude": lat, "longitude": lon},
            "summary": f"Current weather in {name}, {country}: {condition}, {temp_c}°C ({temp_f}°F), wind speed {wind_speed} km/h.",
        }
    except Exception as exc:
        return {"error": f"Failed to fetch live weather for '{location}': {str(exc)}"}
