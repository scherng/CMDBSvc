#!/usr/bin/env python3
"""
Automatic Schema Update Script

Synchronizes db_enhanced_schema.py and field_mapping_schema.py with changes in models.py.
Automatically detects new fields, updates schemas while preserving existing metadata.
"""

import ast
import argparse
import re
import sys
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class FieldInfo:
    """Information about a field from the Pydantic model."""
    name: str
    type_annotation: str
    default_value: Any
    description: Optional[str]
    is_required: bool
    is_list: bool
    enum_values: Optional[List[str]] = None


@dataclass
class ModelInfo:
    """Information about a Pydantic model."""
    name: str
    base_name: str  # UserBase, ApplicationBase, etc.
    fields: Dict[str, FieldInfo]
    entity_type: str  # users, applications, devices


class ModelParser:
    """Parses Pydantic models from models.py to extract field information."""

    def __init__(self, models_file: Path):
        self.models_file = models_file
        self.entity_mapping = {
            'UserBase': 'users',
            'ApplicationBase': 'applications',
            'DeviceBase': 'devices'
        }

    def parse_models(self) -> Dict[str, ModelInfo]:
        """Parse all relevant models from models.py."""
        logger.info(f"Parsing models from {self.models_file}")

        with open(self.models_file, 'r') as f:
            content = f.read()

        tree = ast.parse(content)
        models = {}

        # Find all class definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                model_info = self._parse_model_class(node, content)
                if model_info:
                    models[model_info.name] = model_info

        return models

    def _parse_model_class(self, node: ast.ClassDef, content: str) -> Optional[ModelInfo]:
        """Parse a single model class."""
        class_name = node.name

        # Only parse main entity classes (User, Application, Device)
        if class_name not in self.entity_mapping:
            return None

        logger.info(f"Parsing class: {class_name}")

        # Get base class name
        base_name = f"{class_name}Base"
        entity_type = self.entity_mapping[class_name]

        # Parse fields from the class
        fields = self._extract_fields_from_class(node, content)

        return ModelInfo(
            name=class_name,
            base_name=base_name,
            fields=fields,
            entity_type=entity_type
        )

    def _extract_fields_from_class(self, node: ast.ClassDef, content: str) -> Dict[str, FieldInfo]:
        """Extract field information from a class definition."""
        fields = {}

        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                field_name = item.target.id
                field_info = self._parse_field(item, content)
                if field_info:
                    field_info.name = field_name
                    fields[field_name] = field_info

        return fields

    def _parse_field(self, node: ast.AnnAssign, content: str) -> Optional[FieldInfo]:
        """Parse a single field definition."""
        try:
            # Get type annotation
            type_annotation = self._get_type_annotation(node.annotation)

            # Get default value and check if required
            default_value, is_required = self._get_default_and_required(node.value)

            # Check if it's a list type
            is_list = self._is_list_type(node.annotation)

            # Extract description from Field if present
            description = self._extract_description(node.value)

            # Extract enum values if applicable
            enum_values = self._extract_enum_values(node.annotation, content)

            return FieldInfo(
                name="",  # Will be set by caller
                type_annotation=type_annotation,
                default_value=default_value,
                description=description,
                is_required=is_required,
                is_list=is_list,
                enum_values=enum_values
            )
        except Exception as e:
            logger.warning(f"Could not parse field: {e}")
            return None

    def _get_type_annotation(self, annotation) -> str:
        """Convert AST annotation to string."""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Subscript):
            # Handle List[str], Optional[str], etc.
            if isinstance(annotation.value, ast.Name):
                if annotation.value.id == 'List':
                    return f"array[{self._get_type_annotation(annotation.slice)}]"
                elif annotation.value.id == 'Optional':
                    return self._get_type_annotation(annotation.slice)
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)

        return "string"  # Default fallback

    def _get_default_and_required(self, value_node) -> Tuple[Any, bool]:
        """Extract default value and determine if field is required."""
        if value_node is None:
            return None, True

        if isinstance(value_node, ast.Call):
            # Check if it's Field(...)
            if isinstance(value_node.func, ast.Name) and value_node.func.id == 'Field':
                # Look for ... (Ellipsis) in args - indicates required
                for arg in value_node.args:
                    if isinstance(arg, ast.Constant) and arg.value is ...:
                        return None, True

                # Check for default_factory or default values
                for keyword in value_node.keywords:
                    if keyword.arg == 'default_factory':
                        return [], False  # Usually list fields
                    elif keyword.arg == 'default':
                        return self._extract_constant_value(keyword.value), False

                return None, False

        elif isinstance(value_node, ast.Constant):
            return value_node.value, False

        return None, False

    def _is_list_type(self, annotation) -> bool:
        """Check if the type annotation represents a list."""
        if isinstance(annotation, ast.Subscript):
            if isinstance(annotation.value, ast.Name):
                return annotation.value.id == 'List'
        return False

    def _extract_description(self, value_node) -> Optional[str]:
        """Extract description from Field(..., description=...)."""
        if isinstance(value_node, ast.Call) and isinstance(value_node.func, ast.Name):
            if value_node.func.id == 'Field':
                for keyword in value_node.keywords:
                    if keyword.arg == 'description' and isinstance(keyword.value, ast.Constant):
                        return keyword.value.value
        return None

    def _extract_enum_values(self, annotation, content: str) -> Optional[List[str]]:
        """Extract enum values if the type is an enum."""
        if isinstance(annotation, ast.Name):
            enum_name = annotation.id
            # Look for enum definition in content
            enum_pattern = rf'class {enum_name}\(.*?Enum\):(.*?)(?=class|\Z)'
            match = re.search(enum_pattern, content, re.DOTALL)
            if match:
                enum_body = match.group(1)
                values = []
                for line in enum_body.split('\n'):
                    if '=' in line and not line.strip().startswith('#'):
                        parts = line.split('=')
                        if len(parts) >= 2:
                            value = parts[1].strip().strip('"\'')
                            if value and value != '...':
                                values.append(value)
                return values if values else None
        return None

    def _extract_constant_value(self, node) -> Any:
        """Extract constant value from AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.List):
            return []
        return None


class VariationGenerator:
    """Generates field name variations for AI mapping."""

    @staticmethod
    def generate_variations(field_name: str, field_type: str) -> List[str]:
        """Generate common variations for a field name."""
        variations = []

        # Common patterns based on field name
        base_patterns = {
            'name': ['full_name', 'user_name', 'display_name', 'username', 'person_name'],
            'email': ['email_address', 'user_email', 'mail'],
            'team': ['group', 'department', 'division', 'unit', 'org'],
            'hostname': ['computer_name', 'device_name', 'machine_name', 'host'],
            'ip_address': ['ip', 'ip_addr', 'network_address', 'host_ip'],
            'owner': ['owned_by', 'responsible_person', 'manager', 'maintainer'],
            'type': ['category', 'kind', 'classification'],
            'status': ['state', 'condition', 'activity_status']
        }

        # Add base patterns if they exist
        if field_name in base_patterns:
            variations.extend(base_patterns[field_name])

        # Generate variations by adding common prefixes/suffixes
        prefixes = ['user_', 'app_', 'device_', 'system_']
        suffixes = ['_name', '_id', '_type', '_status', '_count', '_address']

        for prefix in prefixes:
            if not field_name.startswith(prefix):
                variations.append(f"{prefix}{field_name}")

        for suffix in suffixes:
            if not field_name.endswith(suffix) and suffix[1:] not in field_name:
                variations.append(f"{field_name}{suffix}")

        # Add underscore variations
        if '_' in field_name:
            # Remove underscores
            variations.append(field_name.replace('_', ''))
            # CamelCase
            parts = field_name.split('_')
            variations.append(''.join(word.capitalize() for word in parts))
            variations.append(parts[0] + ''.join(word.capitalize() for word in parts[1:]))
        else:
            # Add underscores in logical places
            if len(field_name) > 4:
                for i in range(2, len(field_name) - 1):
                    variations.append(f"{field_name[:i]}_{field_name[i:]}")

        # Remove duplicates and the original field name
        variations = list(set(variations))
        if field_name in variations:
            variations.remove(field_name)

        return variations[:10]  # Limit to top 10 variations


class SchemaUpdater:
    """Updates db_enhanced_schema.py with new field information."""

    def __init__(self, schema_file: Path, dry_run: bool = False):
        self.schema_file = schema_file
        self.dry_run = dry_run
        self.changes = []

    def update_schema(self, models: Dict[str, ModelInfo]) -> bool:
        """Update the enhanced schema with new model information."""
        logger.info(f"Updating enhanced schema: {self.schema_file}")

        # Import the schema as a module to get the actual dictionary
        schema_module = self._import_schema_module()
        if not schema_module:
            return False

        current_schema = schema_module.ENHANCED_SCHEMA

        # Update each model
        has_changes = False
        for model_name, model_info in models.items():
            if self._update_model_in_schema(current_schema, model_info):
                has_changes = True

        if has_changes and not self.dry_run:
            # Write back the updated schema
            self._write_updated_schema(current_schema)
            logger.info(f"Updated {self.schema_file}")

        return has_changes

    def _import_schema_module(self):
        """Import the schema file as a module."""
        try:
            spec = importlib.util.spec_from_file_location("enhanced_schema", self.schema_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            logger.error(f"Could not import schema module: {e}")
            return None

    def _update_model_in_schema(self, schema: Dict[str, Any], model_info: ModelInfo) -> bool:
        """Update a specific model's fields in the schema."""
        entity_type = model_info.entity_type
        collections = schema.get("collections", {})

        if entity_type not in collections:
            logger.warning(f"Entity type {entity_type} not found in schema")
            return False

        collection_schema = collections[entity_type]
        existing_fields = collection_schema.get("fields", {})

        has_changes = False

        for field_name, field_info in model_info.fields.items():
            # Skip auto-generated ID fields
            if field_name in ['ci_id', 'user_id', 'app_id', 'device_id']:
                continue

            if field_name not in existing_fields:
                # Add new field
                field_schema = self._create_field_schema(field_info)
                existing_fields[field_name] = field_schema
                self.changes.append(f"Add field {entity_type}.{field_name}")
                has_changes = True
                logger.info(f"Added new field: {entity_type}.{field_name}")
            else:
                # Update existing field if type changed
                existing_type = existing_fields[field_name].get("type", "string")
                new_type = self._map_python_type_to_schema(field_info.type_annotation)

                if existing_type != new_type:
                    existing_fields[field_name]["type"] = new_type
                    self.changes.append(f"Update field type {entity_type}.{field_name}: {existing_type} -> {new_type}")
                    has_changes = True
                    logger.info(f"Updated field type: {entity_type}.{field_name}")

        return has_changes

    def _create_field_schema(self, field_info: FieldInfo) -> Dict[str, Any]:
        """Create schema entry for a new field."""
        schema = {
            "type": self._map_python_type_to_schema(field_info.type_annotation),
            "description": field_info.description or f"Field: {field_info.name}",
            "required": field_info.is_required
        }

        if field_info.default_value is not None:
            schema["default"] = field_info.default_value

        if field_info.enum_values:
            schema["enum"] = field_info.enum_values

        return schema

    def _map_python_type_to_schema(self, python_type: str) -> str:
        """Map Python type annotations to schema types."""
        type_mapping = {
            "str": "string",
            "int": "number",
            "float": "number",
            "bool": "boolean",
            "datetime": "datetime",
            "array[str]": "array[string]",
            "array[int]": "array[number]"
        }
        return type_mapping.get(python_type.lower(), "string")

    def _write_updated_schema(self, schema: Dict[str, Any]):
        """Write the updated schema back to the file."""
        # Read the original file to preserve imports and structure
        with open(self.schema_file, 'r') as f:
            original_content = f.read()

        # Find where ENHANCED_SCHEMA starts
        schema_start = original_content.find('ENHANCED_SCHEMA = {')
        if schema_start == -1:
            logger.error("Could not find ENHANCED_SCHEMA assignment in file")
            return

        # Preserve everything before the schema
        prefix = original_content[:schema_start]

        # Find everything after the schema (functions, etc.)
        brace_count = 0
        schema_end = schema_start
        in_schema = False

        for i, char in enumerate(original_content[schema_start:], schema_start):
            if char == '{':
                brace_count += 1
                in_schema = True
            elif char == '}' and in_schema:
                brace_count -= 1
                if brace_count == 0:
                    schema_end = i + 1
                    break

        suffix = original_content[schema_end:]

        # Generate the new schema content
        new_schema_content = self._format_schema_dict(schema)

        # Combine everything
        updated_content = prefix + f"ENHANCED_SCHEMA = {new_schema_content}" + suffix

        # Write back to file
        with open(self.schema_file, 'w') as f:
            f.write(updated_content)

    def _format_schema_dict(self, schema: Dict[str, Any], indent: int = 0) -> str:
        """Format the schema dictionary as pretty Python code."""
        import json

        # Use JSON for pretty formatting, then convert to Python syntax
        json_str = json.dumps(schema, indent=4, ensure_ascii=False)

        # Convert JSON booleans to Python booleans
        json_str = json_str.replace('true', 'True').replace('false', 'False').replace('null', 'None')

        return json_str

    def get_changes(self) -> List[str]:
        """Get list of changes that would be made."""
        return self.changes


class FieldMappingUpdater:
    """Updates field_mapping_schema.py with new field information."""

    def __init__(self, schema_file: Path, dry_run: bool = False):
        self.schema_file = schema_file
        self.dry_run = dry_run
        self.changes = []

    def update_field_mapping(self, models: Dict[str, ModelInfo]) -> bool:
        """Update the field mapping schema with new model information."""
        logger.info(f"Updating field mapping schema: {self.schema_file}")

        # Import the field mapping schema as a module
        mapping_module = self._import_mapping_module()
        if not mapping_module:
            return False

        current_schema = mapping_module.FIELD_MAPPING_SCHEMA

        # Update each model
        has_changes = False
        for model_name, model_info in models.items():
            if self._update_model_field_mapping(current_schema, model_info):
                has_changes = True

        if has_changes and not self.dry_run:
            # Write back the updated schema
            self._write_updated_mapping(current_schema)
            logger.info(f"Updated {self.schema_file}")

        return has_changes

    def _import_mapping_module(self):
        """Import the field mapping schema file as a module."""
        try:
            spec = importlib.util.spec_from_file_location("field_mapping_schema", self.schema_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            logger.error(f"Could not import field mapping module: {e}")
            return None

    def _update_model_field_mapping(self, schema: Dict[str, Any], model_info: ModelInfo) -> bool:
        """Update field mappings for a specific model."""
        entity_type = model_info.entity_type

        if entity_type not in schema:
            logger.warning(f"Entity type {entity_type} not found in field mapping schema")
            return False

        canonical_fields = schema[entity_type]["canonical_fields"]
        has_changes = False

        for field_name, field_info in model_info.fields.items():
            # Skip auto-generated ID fields
            if field_name in ['ci_id', 'user_id', 'app_id', 'device_id']:
                continue

            if field_name not in canonical_fields:
                # Add new field mapping
                field_mapping = self._create_field_mapping(field_info)
                canonical_fields[field_name] = field_mapping
                self.changes.append(f"Add field mapping for {entity_type}.{field_name}")
                has_changes = True
                logger.info(f"Added field mapping: {entity_type}.{field_name}")
            else:
                # Update existing field if type changed
                existing_type = canonical_fields[field_name].get("type", "string")
                new_type = self._map_python_type_to_mapping(field_info.type_annotation)

                if existing_type != new_type:
                    canonical_fields[field_name]["type"] = new_type
                    self.changes.append(f"Update field mapping type {entity_type}.{field_name}: {existing_type} -> {new_type}")
                    has_changes = True
                    logger.info(f"Updated field mapping type: {entity_type}.{field_name}")

        return has_changes

    def _create_field_mapping(self, field_info: FieldInfo) -> Dict[str, Any]:
        """Create field mapping entry for a new field."""
        # Generate variations for the field
        variations = VariationGenerator.generate_variations(field_info.name, field_info.type_annotation)

        mapping = {
            "description": field_info.description or f"Field: {field_info.name}",
            "variations": variations,
            "type": self._map_python_type_to_mapping(field_info.type_annotation),
            "required": field_info.is_required
        }

        if field_info.default_value is not None:
            mapping["default"] = field_info.default_value

        if field_info.enum_values:
            mapping["enum"] = field_info.enum_values

        return mapping

    def _map_python_type_to_mapping(self, python_type: str) -> str:
        """Map Python type annotations to field mapping types."""
        type_mapping = {
            "str": "string",
            "int": "number",
            "float": "number",
            "bool": "boolean",
            "datetime": "datetime",
            "array[str]": "array[string]",
            "array[int]": "array[number]"
        }
        return type_mapping.get(python_type.lower(), "string")

    def _write_updated_mapping(self, schema: Dict[str, Any]):
        """Write the updated field mapping back to the file."""
        # Read the original file to preserve imports and structure
        with open(self.schema_file, 'r') as f:
            original_content = f.read()

        # Find where FIELD_MAPPING_SCHEMA starts
        schema_start = original_content.find('FIELD_MAPPING_SCHEMA = {')
        if schema_start == -1:
            logger.error("Could not find FIELD_MAPPING_SCHEMA assignment in file")
            return

        # Preserve everything before the schema
        prefix = original_content[:schema_start]

        # Find everything after the schema (functions, etc.)
        brace_count = 0
        schema_end = schema_start
        in_schema = False

        for i, char in enumerate(original_content[schema_start:], schema_start):
            if char == '{':
                brace_count += 1
                in_schema = True
            elif char == '}' and in_schema:
                brace_count -= 1
                if brace_count == 0:
                    schema_end = i + 1
                    break

        suffix = original_content[schema_end:]

        # Generate the new schema content
        new_schema_content = self._format_mapping_dict(schema)

        # Combine everything
        updated_content = prefix + f"FIELD_MAPPING_SCHEMA = {new_schema_content}" + suffix

        # Write back to file
        with open(self.schema_file, 'w') as f:
            f.write(updated_content)

    def _format_mapping_dict(self, schema: Dict[str, Any]) -> str:
        """Format the field mapping dictionary as pretty Python code."""
        import json

        # Use JSON for pretty formatting, then convert to Python syntax
        json_str = json.dumps(schema, indent=4, ensure_ascii=False)

        # Convert JSON booleans to Python booleans
        json_str = json_str.replace('true', 'True').replace('false', 'False').replace('null', 'None')

        return json_str

    def get_changes(self) -> List[str]:
        """Get list of changes that would be made."""
        return self.changes


def main():
    """Main function with CLI interface."""
    parser = argparse.ArgumentParser(description='Update schema files from models.py')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without making them')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    parser.add_argument('--models-file', default='app/db/models.py', help='Path to models.py file')
    parser.add_argument('--enhanced-schema', default='app/core/llm_data/db_enhanced_schema.py',
                       help='Path to enhanced schema file')
    parser.add_argument('--field-mapping', default='app/core/llm_data/field_mapping_schema.py',
                       help='Path to field mapping schema file')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate file paths
    models_file = Path(args.models_file)
    enhanced_schema_file = Path(args.enhanced_schema)
    field_mapping_file = Path(args.field_mapping)

    for file_path in [models_file, enhanced_schema_file, field_mapping_file]:
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            sys.exit(1)

    try:
        # Parse models
        parser = ModelParser(models_file)
        models = parser.parse_models()

        if not models:
            logger.info("No models found to process")
            return

        logger.info(f"Found {len(models)} models: {list(models.keys())}")

        # Update enhanced schema
        schema_updater = SchemaUpdater(enhanced_schema_file, dry_run=args.dry_run)
        enhanced_changes = schema_updater.update_schema(models)

        # Update field mapping
        mapping_updater = FieldMappingUpdater(field_mapping_file, dry_run=args.dry_run)
        mapping_changes = mapping_updater.update_field_mapping(models)

        # Report results
        if args.dry_run:
            print("\n=== DRY RUN - NO CHANGES MADE ===")

        print(f"\nEnhanced Schema Changes ({len(schema_updater.get_changes())}):")
        for change in schema_updater.get_changes():
            print(f"  • {change}")

        print(f"\nField Mapping Changes ({len(mapping_updater.get_changes())}):")
        for change in mapping_updater.get_changes():
            print(f"  • {change}")

        if not enhanced_changes and not mapping_changes:
            print("\n✅ No changes needed - schemas are up to date!")
        elif args.dry_run:
            print(f"\n📝 Would make {len(schema_updater.get_changes()) + len(mapping_updater.get_changes())} changes")
        else:
            print(f"\n✅ Successfully updated schemas with {len(schema_updater.get_changes()) + len(mapping_updater.get_changes())} changes")

    except Exception as e:
        logger.error(f"Error updating schemas: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()