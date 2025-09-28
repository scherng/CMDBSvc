#!/usr/bin/env python3
"""
Test script for LLM Field Mapping functionality

This script tests the AI-enhanced field mapping capabilities to ensure
field name variations are properly mapped to canonical fields.
"""

import asyncio
import json
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.ingest.field_normalizer import FieldNormalizer
from app.core.llm_service import llm_service


def print_mapping_result(result, test_name):
    """Pretty print mapping results."""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")

    print(f"Entity Type: {result.entity_type}")
    print(f"Confidence Score: {result.confidence_score:.2f}")
    print(f"Mapped Fields: {len(result.mapped_data)}")
    print(f"Unmapped Fields: {len(result.unmapped_fields)}")

    print(f"\nField Mappings:")
    for mapping in result.mappings:
        status = "✓" if mapping.canonical_field else "✗"
        confidence = f"({mapping.confidence:.2f})" if mapping.canonical_field else ""
        print(f"  {status} {mapping.original_field} → {mapping.canonical_field or 'UNMAPPED'} {confidence}")
        print(f"    Reasoning: {mapping.reasoning}")

    print(f"\nMapped Data:")
    for key, value in result.mapped_data.items():
        print(f"  {key}: {value}")

    if result.unmapped_fields:
        print(f"\nUnmapped Fields: {result.unmapped_fields}")


async def test_user_field_variations():
    """Test user entity with various field name variations."""
    mapper = FieldNormalizer()

    # Test data with field variations
    user_data = {
        "full_name": "John Doe",              # Should map to "name"
        "email_address": "john@company.com",   # Should map to "email"
        "mfa_status": True,                    # Should map to "mfa_enabled"
        "group": "Engineering",                # Should map to "team"
        "last_sign_in": "2024-01-15",         # Should map to "last_login"
        "app_assignments": ["app1", "app2"],   # Should map to "assigned_application_ids"
        "unknown_field": "some_value"          # Should remain unmapped
    }

    result = await mapper.detect_and_normalize(user_data)
    print_mapping_result(result, "User Field Variations")

    return result


async def test_application_field_variations():
    """Test application entity with various field name variations."""
    mapper = FieldNormalizer()

    # Test data with field variations
    app_data = {
        "application_name": "CRM System",      # Should map to "name"
        "app_type": "web",                     # Should map to "type"
        "owned_by": "Alice Smith",             # Should map to "owner"
        "usage_stats": 1500,                   # Should map to "usage_count"
        "connected_systems": ["ldap", "sso"],  # Should map to "integrations"
        "user_assignments": ["user1", "user2"], # Should map to "user_ids"
        "custom_field": "special_value"        # Should remain unmapped
    }

    result = await mapper.detect_and_normalize(app_data)
    print_mapping_result(result, "Application Field Variations")

    return result


async def test_device_field_variations():
    """Test device entity with various field name variations."""
    mapper = FieldNormalizer()

    # Test data with field variations
    device_data = {
        "machine_name": "LAPTOP-001",          # Should map to "hostname"
        "ip": "192.168.1.100",                 # Should map to "ip_address"
        "operating_system": "Windows 11",      # Should map to "os"
        "user_assigned": "john.doe",           # Should map to "assigned_user"
        "physical_location": "Office Floor 2", # Should map to "location"
        "device_status": "active",             # Should map to "status"
        "serial_number": "ABC123XYZ"           # Should remain unmapped if not canonical
    }

    result = await mapper.detect_and_normalize(device_data)
    print_mapping_result(result, "Device Field Variations")

    return result


async def test_mixed_confidence_mapping():
    """Test data that should produce mixed confidence scores."""
    mapper = FieldNormalizer(confidence_threshold=0.8)  # Higher threshold

    mixed_data = {
        "name": "Exact Match",                 # Should be high confidence
        "usr_email": "test@example.com",       # Should be medium confidence
        "mfa": True,                           # Should be medium confidence
        "xyz_field": "unknown",                # Should be low/no confidence
        "team_name": "DevOps"                  # Should be medium confidence
    }

    result = await mapper.detect_and_normalize(mixed_data)
    print_mapping_result(result, "Mixed Confidence Mapping (threshold=0.8)")

    return result


async def test_exact_match_fallback():
    """Test fallback to exact matching when AI is disabled."""
    mapper = FieldNormalizer()
    mapper.enabled = False  # Disable AI

    fallback_data = {
        "name": "Direct Match",                # Should map exactly
        "email": "exact@example.com",          # Should map exactly
        "unknown_variation": "test",           # Should remain unmapped
        "team": "Engineering"                  # Should map exactly
    }

    result = await mapper.normalize_fields(fallback_data, "users")
    print_mapping_result(result, "Exact Match Fallback (AI Disabled)")

    return result


async def test_entity_type_detection():
    """Test AI entity type detection with different data patterns."""
    mapper = FieldNormalizer()

    test_cases = [
        {
            "data": {"mfa_enabled": True, "team": "IT", "last_login": "2024-01-01"},
            "expected": "users"
        },
        {
            "data": {"usage_count": 100, "integrations": ["sso"], "owner": "admin"},
            "expected": "applications"
        },
        {
            "data": {"hostname": "server-01", "ip_address": "10.0.0.1", "os": "Linux"},
            "expected": "devices"
        }
    ]

    print(f"\n{'='*60}")
    print(f"TEST: Entity Type Detection")
    print(f"{'='*60}")

    for i, case in enumerate(test_cases, 1):
        try:
            result = await mapper.detect_and_normalize(case["data"])
            status = "✓" if result.entity_type == case["expected"] else "✗"
            print(f"  Case {i}: {status} Detected: {result.entity_type}, Expected: {case['expected']}")
            print(f"    Data: {case['data']}")
        except Exception as e:
            print(f"  Case {i}: ✗ Error: {e}")

    return True


async def main():
    """Run all test cases."""
    print("LLM Field Mapping Test Suite")
    print("=" * 60)

    # Check if LLM service is available
    if not llm_service.is_available():
        print("❌ LLM Service not available - check API key in settings")
        print("   The tests will use fallback exact matching only")
        print()
    else:
        print("✅ LLM Service available")
        print()

    try:
        # Run all tests
        await test_user_field_variations()
        await test_application_field_variations()
        await test_device_field_variations()
        await test_mixed_confidence_mapping()
        await test_exact_match_fallback()
        await test_entity_type_detection()

        print(f"\n{'='*60}")
        print("All tests completed!")
        print(f"{'='*60}")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())