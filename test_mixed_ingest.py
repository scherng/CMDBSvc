#!/usr/bin/env python3
"""
Test script to verify mixed entity ingestion works correctly.
"""

import requests
import json
from datetime import datetime

# API endpoint
BASE_URL = "http://localhost:8000"
INGEST_URL = f"{BASE_URL}/ingest"

def test_mixed_entity_ingest():
    """Test ingesting a mix of users and applications in a single request."""

    # Mixed data payload with both users and applications
    payload = {
        "data": [
            # User 1
            {
                "name": "Alice Smith",
                "team": "Engineering",
                "mfa_enabled": True,
                "last_login": "2024-01-15T10:30:00Z"
            },
            # Application 1
            {
                "name": "Customer Portal",
                "owner": "Web Team",
                "type": "SaaS",
                "integrations": ["Auth0", "Stripe"],
                "usage_count": 1500
            },
            # User 2
            {
                "name": "Bob Johnson",
                "team": "DevOps",
                "mfa_enabled": False
            },
            # Application 2
            {
                "name": "Analytics Dashboard",
                "owner": "Data Team",
                "type": "on-prem",
                "integrations": ["PostgreSQL", "Redis"],
                "usage_count": 250
            },
            # User 3
            {
                "name": "Charlie Davis",
                "team": "Security",
                "mfa_enabled": True,
                "last_login": "2024-01-20T14:45:00Z"
            }
        ],
        "metadata": {
            "source": "test_script",
            "timestamp": datetime.now().isoformat()
        }
    }

    print("=" * 60)
    print("Testing Mixed Entity Ingestion")
    print("=" * 60)
    print(f"\nSending {len(payload['data'])} items (3 users, 2 applications)...")

    try:
        # Send POST request
        response = requests.post(
            INGEST_URL,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        # Check response
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Success! All entities created:")
            print("-" * 40)

            users = []
            apps = []

            for item in result['results']:
                if item['entity_type'] == 'user':
                    users.append(item)
                else:
                    apps.append(item)

                print(f"\n{item['entity_type'].upper()}: {item['ci_id']}")
                print(f"  Entity ID: {item['entity_id']}")
                print(f"  Message: {item['message']}")

            print("\n" + "=" * 60)
            print(f"Summary: Created {len(users)} users and {len(apps)} applications")
            print("=" * 60)

        else:
            print(f"\n❌ Error: Status code {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API.")
        print("Make sure the FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

def test_list_entities():
    """Test listing the created entities."""
    print("\n" + "=" * 60)
    print("Listing Created Entities")
    print("=" * 60)

    # List users
    try:
        response = requests.get(f"{BASE_URL}/users?limit=5")
        if response.status_code == 200:
            users = response.json()
            print(f"\n📋 Users ({len(users)} found):")
            for user in users:
                print(f"  - {user['name']} (Team: {user['team']}, MFA: {user['mfa_enabled']})")
    except Exception as e:
        print(f"Error listing users: {e}")

    # List applications
    try:
        response = requests.get(f"{BASE_URL}/apps?limit=5")
        if response.status_code == 200:
            apps = response.json()
            print(f"\n📋 Applications ({len(apps)} found):")
            for app in apps:
                print(f"  - {app['name']} (Owner: {app['owner']}, Type: {app['type']})")
    except Exception as e:
        print(f"Error listing applications: {e}")

if __name__ == "__main__":
    print("\n🚀 Testing Mixed Entity Ingestion API")
    print("Make sure the FastAPI server is running first!\n")

    # Test mixed ingestion
    test_mixed_entity_ingest()

    # List created entities
    test_list_entities()

    print("\n✨ Test completed!\n")