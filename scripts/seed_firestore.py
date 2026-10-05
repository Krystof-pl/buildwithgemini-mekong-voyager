#!/usr/bin/env python3
"""Seed script for populating Firestore with Vietnam & SEA destinations data."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-49140da9fb98"
COLLECTION_NAME = "destinations"

SEED_DESTINATIONS = [
    {
        "id": "ha-long-bay",
        "name": "Ha Long Bay",
        "country": "Vietnam",
        "region": "Northern Vietnam",
        "description": "UNESCO World Heritage site known for emerald waters and thousands of towering limestone karst islands topped by rainforests.",
        "category": "Nature & Cruise",
        "best_season": "October to April",
        "estimated_daily_budget_usd": 90,
        "highlights": ["Overnight junk boat cruise", "Luon Cave kayaking", "Ti Top Island view"],
    },
    {
        "id": "hoi-an",
        "name": "Hoi An Ancient Town",
        "country": "Vietnam",
        "region": "Central Vietnam",
        "description": "Exceptionally well-preserved trading port dating from the 15th to 19th century, famous for lantern-lit streets, historic architecture, and custom tailors.",
        "category": "Culture & Dining",
        "best_season": "February to July",
        "estimated_daily_budget_usd": 50,
        "highlights": ["Japanese Covered Bridge", "Night market lanterns", "Cao Lau noodle tasting", "Custom tailoring"],
    },
    {
        "id": "sapa-valley",
        "name": "Sapa Valley",
        "country": "Vietnam",
        "region": "Northern Vietnam",
        "description": "Picturesque mountain town overlooking terraced rice paddies, home to diverse ethnic minority hill tribes and Mount Fansipan.",
        "category": "Trekking & Adventure",
        "best_season": "September to November, March to May",
        "estimated_daily_budget_usd": 45,
        "highlights": ["Muong Hoa Valley trekking", "Fansipan Cable Car", "Homestay with Hmong family"],
    },
    {
        "id": "angkor-wat",
        "name": "Angkor Wat & Siem Reap",
        "country": "Cambodia",
        "region": "Siem Reap",
        "description": "Massive 12th-century temple complex and the largest religious monument in the world, iconic symbol of Cambodian heritage.",
        "category": "Culture & History",
        "best_season": "November to March",
        "estimated_daily_budget_usd": 65,
        "highlights": ["Sunrise over Angkor Wat", "Ta Prohm jungle temple", "Tonle Sap floating village"],
    },
    {
        "id": "luang-prabang",
        "name": "Luang Prabang",
        "country": "Laos",
        "region": "Northern Laos",
        "description": "Charming UNESCO town surrounded by jungle-covered mountains, famous for French colonial architecture, night markets, and Kuang Si Falls.",
        "category": "Nature & Heritage",
        "best_season": "November to February",
        "estimated_daily_budget_usd": 55,
        "highlights": ["Kuang Si Waterfalls", "Alms giving ceremony", "Mount Phousi sunset"],
    },
]


def seed_firestore():
    print(f"Connecting to Firestore for project '{PROJECT_ID}'...")
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection(COLLECTION_NAME)

    for dest in SEED_DESTINATIONS:
        doc_id = dest["id"]
        doc_data = {k: v for k, v in dest.items() if k != "id"}
        collection_ref.document(doc_id).set(doc_data)
        print(f"  ✓ Seeded document: {doc_id} ({dest['name']})")

    print(f"\nSuccessfully seeded {len(SEED_DESTINATIONS)} destinations into collection '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    seed_firestore()
