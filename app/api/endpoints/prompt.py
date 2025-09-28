from fastapi import APIRouter, HTTPException
from app.core.prompt.llm_query_handler import LLMToDbQueryHandler
from app.db.db_factory import DatabaseFactory

from pydantic import BaseModel
import logging
from typing import Dict, Any

router = APIRouter()

logger = logging.getLogger(__name__)

class PromptRequest(BaseModel):
      prompt: str

class PromptResponse(BaseModel):
    original_prompt: str
    mongo_query: Dict[str, Any]
    execution: Dict[str, Any]

@router.post("/ask", response_model=Dict[str,Any])
async def query_from_prompt(request: PromptRequest):

    logger.info(f"Going to ask LLM the question: {request.prompt}")
    try:
        # Get the database instance from factory
        database = DatabaseFactory.get_database()

        # Create LLM handler with database dependency
        llm_handler = LLMToDbQueryHandler(database)

        # Process the prompt and execute the query
        result = llm_handler.prompt(request.prompt)

        logger.info(f"Finished operation, result: {result.get('execution', {}).get('count', 'unknown')} records")
        return result
    except RuntimeError as e:
        # Database not initialized
        raise HTTPException(
            status_code=503,
            detail=f"Database not available: {str(e)}"
        )
    except HTTPException:
        # Rethrow HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing prompt request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to handle ask due to {str(e)}"
        )
    
