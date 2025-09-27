from typing import Any, Dict, Optional
import json
from .base import BaseExtractor


class AIExtractor(BaseExtractor):
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key
        
    async def extract(self, raw_data: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        
        if not self.validate_input(raw_data):
            raise ValueError("Invalid input data format")
        
        extracted_data = {
            "entity_type": self._identify_entity_type(raw_data),
            "key_attributes": self._extract_key_attributes(raw_data),
            "relationships": self._extract_relationships(raw_data),
            "metadata": self._extract_metadata(raw_data)
        }
        
        #TODO review optuons
        # if config and config.get("use_ai", False) and self.api_key:
        #     extracted_data = await self._ai_enhanced_extraction(raw_data, config)
        
        return extracted_data
    
    def validate_input(self, raw_data: Dict[str, Any]) -> bool:
        return isinstance(raw_data, dict) and len(raw_data) > 0
    
    def _identify_entity_type(self, raw_data: Dict[str, Any]) -> str:
        if "type" in raw_data:
            return raw_data["type"]
        elif "entity_type" in raw_data:
            return raw_data["entity_type"]
        elif "class" in raw_data:
            return raw_data["class"]
        return "unknown"
    
    def _extract_key_attributes(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        key_fields = ["id", "name", "identifier", "uuid", "key", "title", "label"]
        attributes = {}
        
        for field in key_fields:
            if field in raw_data:
                attributes[field] = raw_data[field]
        
        return attributes
    
    def _extract_relationships(self, raw_data: Dict[str, Any]) -> list:
        relationship_fields = ["parent", "children", "related", "dependencies", "references"]
        relationships = []
        
        for field in relationship_fields:
            if field in raw_data:
                relationships.append({
                    "type": field,
                    "targets": raw_data[field] if isinstance(raw_data[field], list) else [raw_data[field]]
                })
        
        return relationships
    
    def _extract_metadata(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        meta_fields = ["created", "updated", "version", "author", "source", "tags"]
        metadata = {}
        
        for field in meta_fields:
            if field in raw_data:
                metadata[field] = raw_data[field]
        
        return metadata
    
    async def _ai_enhanced_extraction(self, raw_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "entity_type": self._identify_entity_type(raw_data),
            "key_attributes": self._extract_key_attributes(raw_data),
            "relationships": self._extract_relationships(raw_data),
            "metadata": self._extract_metadata(raw_data),
            "ai_extracted": {
                "confidence": 0.95,
                "model": self.model_name,
                "additional_fields": {}
            }
        }