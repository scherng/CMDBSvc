"""
Field Mapping Schema for AI-Enhanced Entity Parser

Defines canonical field names and their common variations to help the AI field mapper
understand which incoming field names should map to which standardized fields.

Define functions needed for the main field mapper logic
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

FIELD_MAPPING_SCHEMA = {
    "users": {
        "description": "User entity field mappings",
        "canonical_fields": {
            "name": {
                "description": "Full name of the user",
                "variations": [
                    "full_name",
                    "user_name",
                    "display_name",
                    "username",
                    "first_name_last_name",
                    "employee_name",
                    "person_name"
                ],
                "type": "string",
                "required": True
            },
            "team": {
                "description": "Team or department the user belongs to",
                "variations": [
                    "group",
                    "department",
                    "division",
                    "unit",
                    "org",
                    "organization",
                    "dept",
                    "team_name",
                    "work_group"
                ],
                "type": "string",
                "required": False
            },
            "mfa_enabled": {
                "description": "Multi-factor authentication enabled status",
                "variations": [
                    "mfa_status",
                    "mfa",
                    "multi_factor_auth",
                    "two_factor",
                    "2fa",
                    "multi_factor_enabled",
                    "mfa_active",
                    "has_mfa",
                    "two_factor_enabled",
                    "multi_factor_authentication"
                ],
                "type": "boolean",
                "required": False,
                "default": False
            },
            "last_login": {
                "description": "Timestamp of user's last login",
                "variations": [
                    "last_access",
                    "last_signin",
                    "last_logged_in",
                    "last_sign_in",
                    "previous_login",
                    "recent_login",
                    "last_activity",
                    "last_access_time"
                ],
                "type": "datetime",
                "required": False
            },
            "assigned_application_ids": {
                "description": "List of application IDs assigned to this user",
                "variations": [
                    "apps",
                    "applications",
                    "app_list",
                    "assigned_apps",
                    "user_applications",
                    "application_access",
                    "app_ids",
                    "accessible_applications",
                    "permitted_apps"
                ],
                "type": "array[string]",
                "required": False,
                "default": []
            },
            "permission_group": {
                "description": "User's provisioned permission, it has to be array",
                "variations": [
                    "permissionGroup",
                    "permissiongroup",
                    "group",
                    "PermissionGroup",
                    "permission_group_type",
                    "permissions",
                    "app_permission_group"
                ],
                "type": "array[string]",
                "required": False,
                "default": []
            }
        }
    },
    "applications": {
        "description": "Application entity field mappings",
        "canonical_fields": {
            "name": {
                "description": "Application name",
                "variations": [
                    "app_name",
                    "application_name",
                    "title",
                    "software_name",
                    "system_name",
                    "service_name",
                    "product_name"
                ],
                "type": "string",
                "required": True
            },
            "owner": {
                "description": "Application owner or responsible person",
                "variations": [
                    "owned_by",
                    "responsible_person",
                    "manager",
                    "maintainer",
                    "admin",
                    "administrator",
                    "contact",
                    "responsible_team",
                    "app_owner",
                    "system_owner",
                    "tech_lead"
                ],
                "type": "string",
                "required": True
            },
            "type": {
                "description": "Application deployment type",
                "variations": [
                    "deployment_type",
                    "app_type",
                    "category",
                    "kind",
                    "application_type",
                    "hosting_type",
                    "environment_type",
                    "platform_type",
                    "service_type"
                ],
                "type": "string",
                "required": False,
                "default": "SaaS",
                "enum": [
                    "SaaS",
                    "on-prem"
                ]
            },
            "usage_count": {
                "description": "Number of times application has been accessed",
                "variations": [
                    "usage",
                    "access_count",
                    "hits",
                    "usage_stats",
                    "access_frequency",
                    "hit_count",
                    "usage_metrics",
                    "activity_count",
                    "login_count"
                ],
                "type": "number",
                "required": False,
                "default": 0
            },
            "integrations": {
                "description": "List of integrated systems or APIs",
                "variations": [
                    "integrated_systems",
                    "connections",
                    "apis",
                    "connectors",
                    "external_systems",
                    "third_party_integrations",
                    "api_connections",
                    "system_integrations",
                    "linked_services"
                ],
                "type": "array[string]",
                "required": False,
                "default": []
            }
        }
    },
    "devices": {
        "description": "Device entity field mappings",
        "canonical_fields": {
            "hostname": {
                "description": "Device hostname or computer name",
                "variations": [
                    "computer_name",
                    "device_name",
                    "machine_name",
                    "host",
                    "system_name",
                    "node_name"
                ],
                "type": "string",
                "required": True
            },
            "ip_address": {
                "description": "IP address of the device",
                "variations": [
                    "ip",
                    "ip_addr",
                    "network_address",
                    "host_ip",
                    "device_ip",
                    "machine_ip",
                    "ipv4_address"
                ],
                "type": "string",
                "required": True
            },
            "os": {
                "description": "Operating system",
                "variations": [
                    "operating_system",
                    "platform",
                    "os_type",
                    "system_type",
                    "os_name",
                    "operating_sys",
                    "platform_type"
                ],
                "type": "string",
                "required": False,
                "default": "windows",
                "enum": [
                    "windows",
                    "macOS",
                    "ubuntu"
                ]
            },
            "assigned_user": {
                "description": "User ID of the primary assigned user",
                "variations": [
                    "primary_user",
                    "user_id",
                    "owner",
                    "assigned_to",
                    "primary_owner",
                    "device_owner",
                    "responsible_user"
                ],
                "type": "string",
                "required": True
            },
            "location": {
                "description": "Physical location of the device",
                "variations": [
                    "physical_location",
                    "site",
                    "office",
                    "building",
                    "room",
                    "floor",
                    "address",
                    "geographical_location"
                ],
                "type": "string",
                "required": True
            },
            "status": {
                "description": "Current device status",
                "variations": [
                    "state",
                    "device_status",
                    "operational_status",
                    "condition",
                    "activity_status",
                    "power_status",
                    "connection_status"
                ],
                "type": "string",
                "required": False,
                "default": "inactive",
                "enum": [
                    "inactive",
                    "active",
                    "suspended"
                ]
            }
        }
    }
}

@dataclass
class FieldMapping:
    """Represents a field mapping result."""
    original_field: str
    canonical_field: Optional[str]
    confidence: float
    reasoning: str

@dataclass
class MappingResult:
    """Represents the complete mapping result for an entity."""
    entity_type: str
    mapped_data: Dict[str, Any]
    mappings: List[FieldMapping]
    unmapped_fields: List[str]
    confidence_score: float


def get_canonical_fields(entity_type: str) -> Dict[str, Any]:
    """Get canonical fields for a specific entity type."""
    return FIELD_MAPPING_SCHEMA.get(entity_type, {}).get("canonical_fields", {})

def get_field_variations(entity_type: str, canonical_field: str) -> List[str]:
    """Get all variations for a specific canonical field."""
    canonical_fields = get_canonical_fields(entity_type)
    field_info = canonical_fields.get(canonical_field, {})
    return field_info.get("variations", [])

def get_all_variations(entity_type: str) -> Dict[str, List[str]]:
    """Get all field variations for an entity type."""
    canonical_fields = get_canonical_fields(entity_type)
    return {
        canonical_field: field_info.get("variations", [])
        for canonical_field, field_info in canonical_fields.items()
    }

def is_required_field(entity_type: str, canonical_field: str) -> bool:
    """Check if a canonical field is required for the entity type."""
    canonical_fields = get_canonical_fields(entity_type)
    field_info = canonical_fields.get(canonical_field, {})
    return field_info.get("required", False)

def get_field_default(entity_type: str, canonical_field: str) -> Any:
    """Get the default value for a canonical field."""
    canonical_fields = get_canonical_fields(entity_type)
    field_info = canonical_fields.get(canonical_field, {})
    return field_info.get("default", None)

def get_supported_entity_types() -> List[str]:
    """Get list of supported entity types."""
    return list(FIELD_MAPPING_SCHEMA.keys())

def generate_exact_mappings(self, input_fields: List[str], entity_type: str) -> List[FieldMapping]:
        """Generate exact match mappings as fallback."""
        canonical_fields = get_canonical_fields(entity_type)
        mappings = []

        for field in input_fields:
            if field in canonical_fields:
                mapping = FieldMapping(
                    original_field=field,
                    canonical_field=field,
                    confidence=1.0,
                    reasoning="Exact match"
                )
            else:
                mapping = FieldMapping(
                    original_field=field,
                    canonical_field=None,
                    confidence=0.0,
                    reasoning="No exact match found"
                )
            mappings.append(mapping)

        return mappings
