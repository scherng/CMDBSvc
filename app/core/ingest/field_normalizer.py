"""
AI-Enhanced Field Mapper using LlamaIndex

This module provides intelligent field mapping capabilities to handle variations
in incoming field names and map them to canonical field names used by the system.

It also comes with a fallback options
"""

from typing import Dict, Any, List
from llama_index.core.llms import ChatMessage, MessageRole
from ..llm_data.field_mapping_schema import (
    FieldMapping,
    MappingResult,
    get_canonical_fields,
    get_supported_entity_types,
    generate_exact_mappings
)
from ..llm_service import llm_service
import json
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class FieldNormalizer:
    """AI-enhanced field mapper using LlamaIndex and OpenAI."""

    def __init__(self, api_key: str = None, confidence_threshold: float = 0.7, max_retries: int = 2):
        """Initialize the LLM field mapper."""
        # Check if LLM service is available
        if llm_service.is_available():
            self.enabled = True
            logger.info("LLM field mapper initialized with shared LLM service")
        else:
            logger.warning("LLM service not available, disabling LLM features")
            self.enabled = False

        self.mapping_cache: Dict[str, FieldMapping] = {}
        self.confidence_threshold = confidence_threshold
        self.max_retries = max_retries

    async def detect_and_normalize(self, data: Dict[str, Any]) -> MappingResult:
        """
        Detect entity type and normalize field names using AI. Main function in this class

        Args:
            data: Raw input data with potentially non-canonical field names

        Returns:
            MappingResult with entity type, normalized data, and mapping details
        """
        logger.info(f"Processing field mapping for data with {len(data)} fields")
        
        if not self.enabled:
            #no llm enabled, using fallback default
            return self._fallback_detection_and_mapping(data)

        try:
            # First, try to detect entity type using AI
            entity_type = await self._llm_detect_entity_type(data)
            logger.info(f"LLM detected entity type: {entity_type}")

            # Then normalize the fields for that entity type
            mapping_result = await self.normalize_fields(data, entity_type)

            return mapping_result

        except Exception as e:
            logger.error(f"LLM detection failed, falling back to heuristics: {e}")
            # Fallback to exact matching and heuristic detection
            return self._fallback_detection_and_mapping(data)

    async def normalize_fields(self, data: Dict[str, Any], entity_type: str) -> MappingResult:
        """
        Normalize field names for a specific entity type.

        Args:
            data: Input data dictionary
            entity_type: Target entity type ("users", "applications", "devices")

        Returns:
            MappingResult with normalized field names
        """
        if not self.enabled:
            return self._exact_match_only(data, entity_type)

        logger.debug(f"Using LLM to normalize fields for entity type: {entity_type}")

        input_fields = list(data.keys())

        # Try to get mappings from AI
        try:
            mappings = await self._get_llm_field_mappings(input_fields, entity_type)

            # Build the normalized data
            mapped_data = {}
            unmapped_fields = []
            total_confidence = 0

            for mapping in mappings:
                if mapping.canonical_field and mapping.confidence >= self.confidence_threshold:
                    # Use the mapping if confidence is high enough
                    mapped_data[mapping.canonical_field] = data[mapping.original_field]
                    total_confidence += mapping.confidence
                elif mapping.canonical_field is None:
                    # Field couldn't be mapped
                    # TODO Failure can be bucketed separately for manual review. Can build a workflow around it
                    unmapped_fields.append(mapping.original_field)
                    logger.warning(f"Could not map field: {mapping.original_field}")
                else:
                    # Low confidence mapping - keep original field name as a warning
                    # TODO Low confidence can be improved by retrain with higher temperature, or different LLM model
                    unmapped_fields.append(mapping.original_field)
                    logger.warning(f"Low confidence mapping for {mapping.original_field} -> {mapping.canonical_field} (confidence: {mapping.confidence:.2f}, threshold: {self.confidence_threshold})")

            # Calculate overall confidence score
            confidence_score = total_confidence / len(mappings) if mappings else 0

            # Add unmapped fields to mapped_data with original names (for transparency)
            # TODO this information can be used to retrain the prompt or enhance documents
            for field in unmapped_fields:
                if field not in mapped_data:
                    mapped_data[field] = data[field]

            result = MappingResult(
                entity_type=entity_type,
                mapped_data=mapped_data,
                mappings=mappings,
                unmapped_fields=unmapped_fields,
                confidence_score=confidence_score
            )

            logger.info(f"Field mapping completed: {len(mapped_data)} fields mapped, {len(unmapped_fields)} unmapped, confidence: {confidence_score:.2f}")
            return result

        except Exception as e:
            logger.error(f"LLM field mapping failed: {e}, falling back to exact matching")
            return self._exact_match_only(data, entity_type)
    
    def _fallback_detection_and_mapping(self, data: Dict[str, Any]) -> MappingResult:
        """Fallback method using heuristics for entity detection and exact matching."""
        logger.info("Using fallback heuristic entity detection")

        # Simple heuristic entity detection (similar to original logic)
        user_indicators = {"mfa_enabled", "team", "last_login", "assigned_application_ids", "mfa_status", "group"}
        app_indicators = {"usage_count", "integrations", "type", "user_ids", "owner", "owned_by"}
        device_indicators = {"hostname", "ip_address", "os", "assigned_user", "location", "status"}

        user_matches = sum(1 for key in data.keys() if key.lower() in {ind.lower() for ind in user_indicators})
        app_matches = sum(1 for key in data.keys() if key.lower() in {ind.lower() for ind in app_indicators})
        device_matches = sum(1 for key in data.keys() if key.lower() in {ind.lower() for ind in device_indicators})

        # Crude sequential check
        if device_matches > max(user_matches, app_matches):
            entity_type = "devices"
        elif user_matches > app_matches:
            entity_type = "users"
        elif app_matches > user_matches:
            entity_type = "applications"
        else:
            entity_type = "users"  # Default

        logger.info(f"Heuristic detection result: {entity_type}")
        return self._exact_match_only(data, entity_type)
    
    async def _llm_detect_entity_type(self, data: Dict[str, Any]) -> str:
        """Use LLM to detect entity type from field names and values."""

        system_prompt = f"""You are an expert at analyzing data structures for a Configuration Management Database (CMDB).

Analyze the following data fields and determine what type of entity this represents.

Available entity types:
{json.dumps(get_supported_entity_types(), indent=2)}

Entity type descriptions:
- users: People/employees in the system with fields like name, team, mfa_enabled, last_login
- applications: Software systems with fields like name, owner, type, usage_count, integrations
- devices: Physical hardware with fields like hostname, ip_address, os, assigned_user, location

IMPORTANT: Return ONLY the entity type as a single word (users, applications, or devices).
"""

        user_prompt = f"""Analyze these data fields and determine the entity type:

Fields: {list(data.keys())}
Sample values: {json.dumps({k: str(v)[:50] + "..." if len(str(v)) > 50 else v for k, v in list(data.items())[:5]}, indent=2)}

Return only the entity type."""

        logger.info(f"Prompt input {user_prompt}")

        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content=system_prompt),
            ChatMessage(role=MessageRole.USER, content=user_prompt)
        ]

        try:
            llm = llm_service.get_llm()
            if not llm:
                raise ValueError("Field mapping LLM not available")

            response = llm.chat(messages)
            entity_type = response.message.content.strip().lower()

            # Validate the response
            supported_types = get_supported_entity_types()
            if entity_type not in supported_types:
                logger.warning(f"LLM returned unsupported entity type: {entity_type}, defaulting to 'users'")
                entity_type = "users"

            return entity_type

        except Exception as e:
            logger.error(f"LLM entity detection failed: {e}")
            raise

    async def _get_llm_field_mappings(self, input_fields: List[str], entity_type: str) -> List[FieldMapping]:
        """Get corresponding field mappings from LLM for the given input fields."""

        canonical_fields = get_canonical_fields(entity_type)

        system_prompt = f"""You are an expert field mapper for database systems. Map input field names to canonical field names.

Entity type: {entity_type}

Available canonical fields for {entity_type}:
{json.dumps(canonical_fields, indent=2)}

Rules:
1. Map each input field to the most appropriate canonical field, incorporating the type of the fields. An array should map to an array
2. If no good match exists, set canonical_field to null
3. Provide confidence score (0-1) for each mapping
4. Provide brief reasoning for each mapping decision
5. Consider semantic meaning, not just string similarity

Return a JSON array with this structure:
[
  {{
    "original_field": "input_field_name",
    "canonical_field": "canonical_name_or_null",
    "confidence": 0.95,
    "reasoning": "Brief explanation"
  }}
]
"""

        user_prompt = f"""Map these input fields to canonical fields:

Input fields: {json.dumps(input_fields)}

Return the mapping as a JSON array."""

        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content=system_prompt),
            ChatMessage(role=MessageRole.USER, content=user_prompt)
        ]

        try:
            llm = llm_service.get_llm()
            if not llm:
                raise ValueError("Field mapping LLM not available")

            response = llm.chat(messages)
            # Parse the JSON response
            response_text = response.message.content.strip()

            # Extract JSON from response (handle cases where LLM adds extra text)
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1

            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                mappings_data = json.loads(json_str)

                # Convert to FieldMapping objects
                mappings = []
                for mapping_data in mappings_data:
                    mapping = FieldMapping(
                        original_field=mapping_data["original_field"],
                        canonical_field=mapping_data.get("canonical_field"),
                        confidence=mapping_data.get("confidence", 0.5),
                        reasoning=mapping_data.get("reasoning", "LLM mapping")
                    )
                    mappings.append(mapping)

                return mappings
            else:
                raise ValueError("No valid JSON array found in LLM response")

        except Exception as e:
            logger.error(f"Failed to parse LLM mapping response: {e}")
            # Return exact match mappings as fallback
            return generate_exact_mappings(input_fields, entity_type)

    def _exact_match_only(self, data: Dict[str, Any], entity_type: str) -> MappingResult:
        """Fallback to exact matching only."""
        canonical_fields = get_canonical_fields(entity_type)
        mapped_data = {}
        unmapped_fields = []
        mappings = []

        for field, value in data.items():
            if field in canonical_fields:
                mapped_data[field] = value
                mapping = FieldMapping(
                    original_field=field,
                    canonical_field=field,
                    confidence=1.0,
                    reasoning="Exact match (fallback mode)"
                )
            else:
                unmapped_fields.append(field)
                mapped_data[field] = value  # Keep unmapped fields
                mapping = FieldMapping(
                    original_field=field,
                    canonical_field=None,
                    confidence=0.0,
                    reasoning="No exact match (fallback mode)"
                )
            mappings.append(mapping)

        return MappingResult(
            entity_type=entity_type,
            mapped_data=mapped_data,
            mappings=mappings,
            unmapped_fields=unmapped_fields,
            confidence_score=len(mapped_data) / len(data) if data else 0
        )
