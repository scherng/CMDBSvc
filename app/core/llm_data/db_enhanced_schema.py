"""
Enhanced Schema for Configuration Management System
Based on User, Application, and Device Pydantic models
"""
from typing import Dict, List, Any

ENHANCED_SCHEMA = {
    "database_name": "it_asset_management",
    "description": "Configuration Items Management System with Users, Applications, and Devices",
    "collections": {
        "users": {
            "description": "User accounts in the ci system",
            "fields": {
                "_id": {
                    "type": "ObjectId",
                    "description": "MongoDB unique identifier"
                },
                "name": {
                    "type": "string",
                    "description": "Full name of the user",
                    "required": True,
                    "example": "John Doe"
                },
                "team": {
                    "type": "string",
                    "description": "Team or department the user belongs to",
                    "required": False,
                    "example": "Engineering"
                },
                "mfa_enabled": {
                    "type": "boolean",
                    "description": "Multi-factor authentication enabled status",
                    "default": False,
                    "example": True
                },
                "last_login": {
                    "type": "datetime",
                    "description": "Timestamp of user's last login",
                    "required": False,
                    "example": "2024-01-15T10:30:00Z"
                },
                "assigned_application_ids": {
                    "type": "array[string]",
                    "description": "List of application IDs assigned to this user",
                    "default": [],
                    "example": [
                        "APP-ABC123DEF456",
                        "APP-GHI789JKL012"
                    ]
                },
                "ci_id": {
                    "type": "string",
                    "description": "Configuration Item ID (CMDB identifier)",
                    "required": True,
                    "pattern": "CI-[A-F0-9]{12}",
                    "example": "CI-ABC123DEF456"
                },
                "user_id": {
                    "type": "string",
                    "description": "Unique user identifier",
                    "required": True,
                    "pattern": "USR-[A-F0-9]{12}",
                    "example": "USR-123ABC456DEF"
                },
                "permission_group": {
                    "type": "array[string]",
                    "description": "User's provisioned permission",
                    "required": False,
                    "default": []
                }
            },
            "relationships": {
                "applications": "Many-to-many via assigned_application_ids (users.assigned_application_ids -> applications.app_id)",
                "devices": "One-to-many via assigned_user (users.user_id -> devices.assigned_user)"
            },
            "common_queries": [
                "Find users by team",
                "Users with MFA enabled/disabled",
                "Users who haven't logged in recently",
                "Users assigned to specific applications",
                "Active vs inactive users",
                "Users without devices assigned"
            ],
            "business_context": {
                "purpose": "Manage user accounts and their access in the company",
                "compliance": "Track MFA compliance and access patterns",
                "security": "Monitor login patterns and access assignments"
            }
        },
        "applications": {
            "description": "Applications and software systems in the enterprise",
            "fields": {
                "_id": {
                    "type": "ObjectId",
                    "description": "MongoDB unique identifier"
                },
                "name": {
                    "type": "string",
                    "description": "Application name",
                    "required": True,
                    "example": "Slack"
                },
                "owner": {
                    "type": "string",
                    "description": "Application owner or responsible person",
                    "required": True,
                    "example": "Engineering"
                },
                "type": {
                    "type": "string",
                    "description": "Application deployment type",
                    "enum": [
                        "SaaS",
                        "on-prem"
                    ],
                    "default": "SaaS",
                    "example": "SaaS"
                },
                "integrations": {
                    "type": "array[string]",
                    "description": "List of integrated systems or APIs",
                    "default": [],
                    "example": [
                        "LDAP",
                        "SSO",
                        "API-Gateway"
                    ]
                },
                "usage_count": {
                    "type": "number",
                    "description": "Number of times application has been accessed",
                    "default": 0,
                    "example": 1250
                },
                "ci_id": {
                    "type": "string",
                    "description": "Configuration Item ID (CMDB identifier)",
                    "required": True,
                    "pattern": "CI-[A-F0-9]{12}",
                    "example": "CI-APP789XYZ123"
                },
                "app_id": {
                    "type": "string",
                    "description": "Unique application identifier",
                    "required": True,
                    "pattern": "APP-[A-F0-9]{12}",
                    "example": "APP-789XYZ123ABC"
                }
            },
            "relationships": {
                "users": "Many-to-many via user_ids (applications.user_ids -> users.user_id)",
                "reverse_users": "Many-to-many via assigned_application_ids (users.assigned_application_ids -> applications.app_id)"
            },
            "common_queries": [
                "Applications by type (SaaS vs on-prem)",
                "Most used applications",
                "Applications with no users assigned",
                "Applications by owner",
                "Applications with specific integrations",
                "Unused or low-usage applications"
            ],
            "business_context": {
                "purpose": "Track software assets and their usage",
                "cost_management": "Monitor SaaS vs on-premise costs",
                "security": "Track integrations and access patterns"
            }
        },
        "devices": {
            "description": "Physical devices in the enterprise",
            "fields": {
                "_id": {
                    "type": "ObjectId",
                    "description": "MongoDB unique identifier"
                },
                "hostname": {
                    "type": "string",
                    "description": "Device hostname or computer name",
                    "required": True,
                    "example": "LAPTOP-JOHN-001"
                },
                "ip_address": {
                    "type": "string",
                    "description": "IP address of the device",
                    "required": True,
                    "pattern": "^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$",
                    "example": "192.168.1.100"
                },
                "os": {
                    "type": "string",
                    "description": "Operating system",
                    "enum": [
                        "windows",
                        "macOS",
                        "ubuntu"
                    ],
                    "default": "windows",
                    "example": "windows"
                },
                "assigned_user": {
                    "type": "string",
                    "description": "User ID of the primary assigned user",
                    "required": True,
                    "example": "USR-123ABC456DEF"
                },
                "location": {
                    "type": "string",
                    "description": "Physical location of the device",
                    "required": True,
                    "example": "Office Floor 3"
                },
                "status": {
                    "type": "string",
                    "description": "Current device status",
                    "enum": [
                        "inactive",
                        "active",
                        "suspended"
                    ],
                    "default": "inactive",
                    "example": "active"
                },
                "ci_id": {
                    "type": "string",
                    "description": "Configuration Item ID (CMDB identifier)",
                    "required": True,
                    "pattern": "CI-[A-F0-9]{12}",
                    "example": "CI-DEV456ABC789"
                },
                "device_id": {
                    "type": "string",
                    "description": "Unique device identifier",
                    "required": True,
                    "pattern": "DEV-[A-F0-9]{12}",
                    "example": "DEV-456ABC789XYZ"
                },
                "user_ids": {
                    "type": "array[string]",
                    "description": "List of all user IDs who have access to this device",
                    "default": [],
                    "example": [
                        "USR-123ABC456DEF",
                        "USR-GHI789JKL012"
                    ]
                }
            },
            "relationships": {
                "primary_user": "Many-to-one via assigned_user (devices.assigned_user -> users.user_id)",
                "all_users": "Many-to-many via user_ids (devices.user_ids -> users.user_id)"
            },
            "common_queries": [
                "Devices by operating system",
                "Active vs inactive devices",
                "Devices by location",
                "Devices assigned to specific user",
                "Unassigned devices",
                "Devices by IP range",
                "Suspended devices"
            ],
            "business_context": {
                "purpose": "Track physical devices",
                "compliance": "Asset inventory for audits",
                "security": "Monitor device access and status"
            }
        }
    },
    "cross_collection_relationships": {
        "user_application_access": {
            "description": "Users can be assigned to multiple applications",
            "query_pattern": "Find users and their assigned applications",
            "mongodb_lookup": {
                "from_collection": "users",
                "lookup": {
                    "from": "applications",
                    "localField": "assigned_application_ids",
                    "foreignField": "app_id",
                    "as": "assigned_applications"
                }
            }
        },
        "user_device_assignment": {
            "description": "Users can have devices assigned to them",
            "query_pattern": "Find users and their assigned devices",
            "mongodb_lookup": {
                "from_collection": "users",
                "lookup": {
                    "from": "devices",
                    "localField": "user_id",
                    "foreignField": "assigned_user",
                    "as": "assigned_devices"
                }
            }
        },
        "application_user_access": {
            "description": "Applications can have multiple users with access",
            "query_pattern": "Find applications and their users",
            "mongodb_lookup": {
                "from_collection": "applications",
                "lookup": {
                    "from": "users",
                    "localField": "user_ids",
                    "foreignField": "user_id",
                    "as": "application_users"
                }
            }
        }
    },
    "query_patterns": {
        "basic_find": {
            "description": "Simple find queries for individual collections",
            "format": "{\"collection\": \"name\", \"query\": {...}, \"limit\": 10}",
            "examples": [
                "{\"collection\": \"users\", \"query\": {\"mfa_enabled\": True}}",
                "{\"collection\": \"applications\", \"query\": {\"type\": \"SaaS\"}}",
                "{\"collection\": \"devices\", \"query\": {\"status\": \"active\", \"os\": \"windows\"}}"
            ]
        },
        "user_analytics": {
            "description": "Analytics queries for user management",
            "examples": [
                {
                    "description": "Count users by team",
                    "query": {
                        "collection": "users",
                        "pipeline": [
                            {
                                "$group": {
                                    "_id": "$team",
                                    "count": {
                                        "$sum": 1
                                    }
                                }
                            },
                            {
                                "$sort": {
                                    "count": -1
                                }
                            }
                        ]
                    }
                },
                {
                    "description": "MFA compliance rate",
                    "query": {
                        "collection": "users",
                        "pipeline": [
                            {
                                "$group": {
                                    "_id": "$mfa_enabled",
                                    "count": {
                                        "$sum": 1
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        },
        "asset_analytics": {
            "description": "Device analytics and reporting",
            "examples": [
                {
                    "description": "Device distribution by OS",
                    "query": {
                        "collection": "devices",
                        "pipeline": [
                            {
                                "$group": {
                                    "_id": "$os",
                                    "count": {
                                        "$sum": 1
                                    }
                                }
                            },
                            {
                                "$sort": {
                                    "count": -1
                                }
                            }
                        ]
                    }
                }
            ]
        },
        "application_analytics": {
            "description": "Application analytics and reporting query",
            "examples": [
                {
                    "description": "List top Apps with the most integration",
                    "query": {
                        "collection": "applications",
                        "pipeline": [
                            {
                                "$addFields": {
                                    "integration_count": {
                                        "$size": {
                                            "$ifNull": [
                                                "$integrations",
                                                []
                                            ]
                                        }
                                    }
                                }
                            },
                            {
                                "$sort": {
                                    "integration_count": -1
                                }
                            },
                            {
                                "$limit": 10
                            },
                            {
                                "$project": {
                                    "name": 1,
                                    "owner": 1,
                                    "type": 1,
                                    "integrations": 1,
                                    "integration_count": 1,
                                    "usage_count": 1,
                                    "app_id": 1
                                }
                            }
                        ]
                    }
                },
                {
                    "description": "Application usage statistics",
                    "query": {
                        "collection": "applications",
                        "pipeline": [
                            {
                                "$group": {
                                    "_id": "$type",
                                    "total_apps": {
                                        "$sum": 1
                                    },
                                    "avg_usage": {
                                        "$avg": "$usage_count"
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        },
        "security_queries": {
            "description": "Security and compliance related queries",
            "examples": [
                {
                    "description": "Users without MFA who have device access",
                    "query": {
                        "collection": "users",
                        "pipeline": [
                            {
                                "$match": {
                                    "mfa_enabled": False
                                }
                            },
                            {
                                "$lookup": {
                                    "from": "devices",
                                    "localField": "user_id",
                                    "foreignField": "assigned_user",
                                    "as": "devices"
                                }
                            },
                            {
                                "$match": {
                                    "devices": {
                                        "$ne": []
                                    }
                                }
                            }
                        ]
                    }
                },
                {
                    "description": "Inactive devices with active applications",
                    "query": {
                        "collection": "devices",
                        "pipeline": [
                            {
                                "$match": {
                                    "status": "inactive"
                                }
                            },
                            {
                                "$lookup": {
                                    "from": "users",
                                    "localField": "assigned_user",
                                    "foreignField": "user_id",
                                    "as": "user"
                                }
                            },
                            {
                                "$unwind": "$user"
                            },
                            {
                                "$match": {
                                    "user.assigned_application_ids": {
                                        "$ne": []
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }
    },
    "natural_language_examples": {
        "user_queries": [
            "Find all users with MFA enabled",
            "Show users who haven't logged in for 30 days",
            "List users by team",
            "Find users without any applications assigned",
            "Users with more than 5 applications",
            "Show users in the Engineering team"
        ],
        "application_queries": [
            "List all SaaS applications",
            "Find the most used applications",
            "Show applications with no users",
            "Applications owned by a team",
            "Find applications with LDAP integration",
            "Count applications by type"
        ],
        "device_queries": [
            "Show all Windows devices",
            "Find active devices in Office Floor 3",
            "List suspended devices",
            "Devices assigned to John Doe",
            "Find devices without assigned users",
            "Show device distribution by operating system"
        ],
        "cross_collection_queries": [
            "Show users with their assigned applications",
            "Find users and their devices",
            "List applications and their users",
            "Users with both devices and applications",
            "Applications used by users with Windows devices",
            "Teams with the most applications assigned"
        ],
        "analytics_queries": [
            "Count users by team and MFA status",
            "Application usage statistics by type",
            "Device distribution by location and status",
            "Users without MFA who have device access",
            "Most popular applications by usage count",
            "Compliance dashboard for MFA adoption"
        ]
    },
    "data_validation_rules": {
        "users": {
            "required_fields": [
                "name",
                "ci_id",
                "user_id"
            ],
            "unique_fields": [
                "ci_id",
                "user_id"
            ],
            "format_validation": {
                "ci_id": "^CI-[A-F0-9]{12}$",
                "user_id": "^USR-[A-F0-9]{12}$"
            }
        },
        "applications": {
            "required_fields": [
                "name",
                "owner",
                "ci_id",
                "app_id"
            ],
            "unique_fields": [
                "ci_id",
                "app_id"
            ],
            "format_validation": {
                "ci_id": "^CI-[A-F0-9]{12}$",
                "app_id": "^APP-[A-F0-9]{12}$"
            }
        },
        "devices": {
            "required_fields": [
                "hostname",
                "ip_address",
                "assigned_user",
                "location",
                "ci_id",
                "device_id"
            ],
            "unique_fields": [
                "ci_id",
                "device_id",
                "ip_address",
                "hostname"
            ],
            "format_validation": {
                "ci_id": "^CI-[A-F0-9]{12}$",
                "device_id": "^DEV-[A-F0-9]{12}$",
                "ip_address": "^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$"
            }
        }
    }
}

def get_supported_collections() ->  List[str]:
    return ENHANCED_SCHEMA.get("collections", {}).keys()

def get_supported_collections_schemas() -> Dict[str, Any]:
    return ENHANCED_SCHEMA.get("collections")
