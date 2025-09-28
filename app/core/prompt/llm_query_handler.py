from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.llms import ChatMessage, ChatResponse, MessageRole
from llama_index.core import VectorStoreIndex, Settings, Document

from typing import List, Dict, Any, Optional
from pydantic import Field

from app.core.llm_data.db_enhanced_schema import (
    ENHANCED_SCHEMA,
    get_supported_collections,
    get_supported_collections_schemas
)
from .collection_query_router import CollectionQueryRouter
from app.db.connector.database_interface import DatabaseInterface
from app.core.llm_service import llm_service
from app.config.settings import settings

import json
import logging
import openai

openai.api_key = settings.openai_api_key

logger = logging.getLogger(__name__)
# Keep apiKey for backward compatibility and fallback

class LLMToDbQueryHandler:
    def __init__(self, database: DatabaseInterface):
        self.query_engine = SimpleLLMQuery()
        self.query_router = CollectionQueryRouter(database) if database else None
        

    def prompt(self, prompt: str) -> Dict[str, Any]:
        """Process natural language prompt and execute the generated MongoDB query."""
        logger.info("In handlePrompt")
        
        #Defer to QueryEngine for the prompting with LLM
        response = self.query_engine.custom_query(prompt)  # Use the inherited query method from CustomQueryEngine
        result = "error"
        try:
            # Parse the MongoDB query from response
            response_text = response.message.content
            
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                mongo_query = json.loads(json_str)

                # Execute the query using QueryRouter
                execution_result = self.execute_mongo_query(mongo_query)
                logger.info("execute done!")
                result = {
                    "original_prompt": prompt,
                    "mongo_query": mongo_query,
                    "execution": execution_result
                }
            else:
                result = {
                    "error": "Could not parse MongoDB query from LLM response",
                    "raw_response": response_text,
                    "original_prompt": prompt
                }
                
        except Exception as e:
            result = {
                "error": f"Query execution failed: {str(e)}",
                "original_prompt": prompt
            }

        logger.info(f"finished parsing llm output with result: {result}")
        
        # Parse the JSON string back to dict for the API response
        try:
            if "error" not in result and "execution" in result:
                logger.info(f"MongoDB Query: {json.dumps(result['mongo_query'], indent=2)}")
                logger.info(f"Query executed successfully, returned {result['execution'].get('count', 0)} results")
            else:
                logger.info(f"Error or no execution: {result.get('error', 'Unknown error')}")
            return result
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON response: {result}")
            return {"error": "Failed to parse response", "raw_response": result}


    def execute_mongo_query(self, mongo_query: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a MongoDB query using the QueryRouter."""
        try:
            if not self.query_router:
                return {
                    "error": "No database connection available",
                    "query": mongo_query
                }

            return self.query_router.execute(mongo_query)

        except Exception as e:
            logger.error(f"Error executing MongoDB query: {e}")
            return {
                "error": f"Query execution failed: {str(e)}",
                "query": mongo_query
            }
            
# Use a simple vector store index for the LLM prompting
class SimpleLLMQuery():
    def __init__(self):
        self.jsonObj = json.dumps(ENHANCED_SCHEMA, indent=2)
        self.index = VectorStoreIndex.from_documents([Document(text=self.jsonObj)])
        Settings.llm = llm_service.get_llm()
    
    def custom_query(self, query_str: str) -> str:
        retriever = self.index.as_retriever()
        nodes = retriever.retrieve(query_str)
        
        context = "\n\n".join([node.node.text for node in nodes])
        system_prompt = f"""You are a MongoDB query expert. Convert natural language to MongoDB queries.

IMPORTANT RULES:
1. Return ONLY valid JSON in the specified format
2. For simple queries use: {{"collection": "name", "query": {{...}}, "limit": number}}
3. For complex queries use: {{"collection": "name", "pipeline": [...]}}
4. Use proper MongoDB operators: $eq, $gt, $lt, $gte, $lte, $in, $regex, $match, $group, $lookup
5. For text search, use $regex with $options: "i"
6. For ObjectId references, use string format (will be converted)
7. Consider relationships between collections
8. ONLY use the field that are defined in the Collection schemas

Query Classification:
- Simple find: field filters, simple conditions
- Aggregation: joins, grouping, counting, complex transformations

Collections Schema, Context and Examples:
{self.jsonObj}

"""
        user_query = f"Can you convert to MongoDB query: {query_str}"

        # Create messages
        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content=system_prompt),
            ChatMessage(role=MessageRole.USER, content=user_query)
        ]
        
        logger.info("Getting ready for custom query")

        # Get LLM instance from service
        llm = llm_service.get_llm()
        if not llm:
            raise RuntimeError("Query LLM not available - check API key configuration")

        # Get LLM response
        response = llm.chat(messages)
        
        logger.info(f"response is ${response}")

        return response
               
        
# class LLMQueryEngine(CustomQueryEngine):
#     def __init__(self):
#         super().__init__()

#     def custom_query(self, query_str: str) -> str:
#         """Process natural language query and convert to MongoDB"""
#         # Create context-aware prompt        
#         schema_context = json.dumps(ENHANCED_SCHEMA, indent=2)

#         system_prompt = f"""You are a MongoDB query expert. Convert natural language to MongoDB queries.

# IMPORTANT RULES:
# 1. Return ONLY valid JSON in the specified format
# 2. For simple queries use: {{"collection": "name", "query": {{...}}, "limit": number}}
# 3. For complex queries use: {{"collection": "name", "pipeline": [...]}}
# 4. Use proper MongoDB operators: $eq, $gt, $lt, $gte, $lte, $in, $regex, $match, $group, $lookup
# 5. For text search, use $regex with $options: "i"
# 6. For ObjectId references, use string format (will be converted)
# 7. Consider relationships between collections
# 8. ONLY use the field that are defined in the Collection schemas

# Query Classification:
# - Simple find: field filters, simple conditions
# - Aggregation: joins, grouping, counting, complex transformations

# Collections Schema, Context and Examples:
# {schema_context}

# """

# # Available MongoDB Collections:
# # {json.dumps(get_supported_collections(), indent=2)}

#         user_query = f"Convert to MongoDB query: {query_str}"
        
#         # Create messages
#         messages = [
#             ChatMessage(role=MessageRole.SYSTEM, content=system_prompt),
#             ChatMessage(role=MessageRole.USER, content=user_query)
#         ]
        
#         logger.info("Getting ready for custom query")

#         # Get LLM instance from service
#         llm = llm_service.get_llm()
#         if not llm:
#             raise RuntimeError("Query LLM not available - check API key configuration")

#         # Get LLM response
#         response = llm.chat(messages)

#         return response
