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

"""Firestore tools for Mekong Voyager travel concierge agent."""

from typing import Any
from google.cloud import firestore

# Hardcode project ID as string to avoid project-number issues on Agent Engine deployment
PROJECT_ID = "qwiklabs-gcp-03-49140da9fb98"
COLLECTION_NAME = "destinations"

_db_client = None


def get_firestore_client() -> firestore.Client:
    """Lazy-initialize and return the Firestore client with hardcoded project ID."""
    global _db_client
    if _db_client is None:
        _db_client = firestore.Client(project=PROJECT_ID)
    return _db_client


def search_destinations(country: str = "", category: str = "") -> list[dict[str, Any]]:
    """Search travel destinations in Vietnam and Southeast Asia stored in Firestore.

    Args:
        country: Optional country filter (e.g., 'Vietnam', 'Cambodia', 'Laos').
        category: Optional category filter (e.g., 'Nature', 'Culture', 'Mountain', 'Heritage').

    Returns:
        A list of matching destination summary objects.
    """
    db = get_firestore_client()
    collection_ref = db.collection(COLLECTION_NAME)

    results = []
    docs = collection_ref.stream()

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id

        if country and country.lower() not in data.get("country", "").lower():
            continue
        if category and category.lower() not in data.get("category", "").lower():
            continue

        results.append(data)

    return results


def get_destination_details(destination_id: str) -> dict[str, Any]:
    """Retrieve full details for a specific destination from Firestore by its unique ID.

    Args:
        destination_id: Unique identifier for the destination (e.g., 'ha-long-bay', 'hoi-an', 'angkor-wat').

    Returns:
        A dictionary containing full details for the requested destination, or an error message if not found.
    """
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(destination_id)
    doc = doc_ref.get()

    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    else:
        return {"error": f"Destination '{destination_id}' not found in database."}


def add_destination(
    destination_id: str,
    name: str,
    country: str,
    city: str,
    description: str,
    category: str,
    highlights: list[str],
    best_time_to_visit: str,
    average_daily_budget_usd: int,
) -> dict[str, Any]:
    """Add a new travel destination or update an existing one in the Firestore database.

    Args:
        destination_id: Unique slug ID for the destination (e.g. 'phu-quoc', 'hue-city').
        name: Full display name of the destination.
        country: Country name (e.g. 'Vietnam').
        city: City or nearest town.
        description: Rich overview of what makes this destination special.
        category: Travel category (e.g., 'Beach', 'Culture', 'Nature', 'Culinary').
        highlights: List of key attractions and top things to do.
        best_time_to_visit: Ideal months or season to visit.
        average_daily_budget_usd: Estimated daily travel budget per person in USD.

    Returns:
        A confirmation dictionary indicating successful creation or update.
    """
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(destination_id)

    payload = {
        "name": name,
        "country": country,
        "city": city,
        "description": description,
        "category": category,
        "highlights": highlights,
        "best_time_to_visit": best_time_to_visit,
        "average_daily_budget_usd": average_daily_budget_usd,
    }

    doc_ref.set(payload)
    return {
        "status": "success",
        "message": f"Destination '{name}' ({destination_id}) successfully saved to Firestore.",
        "data": payload,
    }
