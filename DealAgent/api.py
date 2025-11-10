"""
FastAPI Server for DealAgent
Exposes DealAgent as HTTP API for UI integration
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import uvicorn
import logging
import sys
import os
from pathlib import Path

# Add the parent directory to Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

# Import the DealAgent
from DealAgent.agent import agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("DealAgent FastAPI application starting")
    yield
    # Shutdown
    logger.info("DealAgent FastAPI application shutting down")

app = FastAPI(lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.get("/")
async def root():
    return {
        "message": "DealAgent API is running. Use /query endpoint to interact with the agent.",
        "endpoints": {
            "POST /query": "Send a query to the DealAgent",
            "GET /docs": "Interactive API documentation"
        }
    }

@app.post("/query")
async def handle_query(request: QueryRequest):
    """Handle queries to the DealAgent."""
    if agent is None:
        raise HTTPException(
            status_code=500,
            detail="Agent is not properly initialized. Please check server logs."
        )
    
    try:
        if not request.query.strip():
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty"
            )
            
        logger.info(f"Processing query: {request.query}")
        
        # Use agent's _iter method which accepts query string directly
        # This is the simplest approach that should work
        response_text = ""
        async for event in agent._iter(request.query):
            # Collect response from different event types
            try:
                # Check for various response attributes
                if hasattr(event, 'response') and event.response:
                    if isinstance(event.response, str):
                        response_text = event.response
                    else:
                        response_text = str(event.response)
                elif hasattr(event, 'text') and event.text:
                    response_text = str(event.text)
                elif hasattr(event, 'content') and event.content:
                    response_text = str(event.content)
                elif hasattr(event, 'message'):
                    msg = event.message
                    if hasattr(msg, 'content'):
                        response_text = str(msg.content)
                    else:
                        response_text = str(msg)
                # Keep the last non-empty response
            except Exception as e:
                logger.debug(f"Error processing event: {e}")
                continue
        
        # Use the final response or default message
        if not response_text:
            response_text = "No response generated"
            
        logger.info("Query processed successfully")
        return {"response": response_text}
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error processing query: {error_msg}")
        
        status_code = 500
        detail = f"Error processing your request: {error_msg}"
        
        if "503" in error_msg or "overloaded" in error_msg.lower():
            status_code = 503
            detail = "The AI service is currently overloaded. Please try again later."
            
        raise HTTPException(
            status_code=status_code,
            detail=detail
        )

if __name__ == "__main__":
    # Start the FastAPI server
    uvicorn.run(
        "DealAgent.api:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )

