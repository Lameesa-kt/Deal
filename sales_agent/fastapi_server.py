from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging
import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

# Now import the agent components
from sales_agent.agent import (
    load_discount_data, 
    load_rebate_data,
    ToolboxClient,
    GoogleGenAI,
    Settings,
    AgentWorkflow,
    PORT
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global agent instance
agent = None

def initialize_agent():
    """Initialize the agent with proper error handling"""
    global agent
    try:
        # Initialize LLM
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set")
        
        llm = GoogleGenAI(model="gemini-2.5-flash", api_key=api_key)
        Settings.llm = llm

        # Initialize Toolbox
        toolbox = ToolboxClient(f"http://127.0.0.1:{PORT}")
        tools = toolbox.load_toolset()
        
        # Add CSV tools
        all_tools = tools + [load_discount_data, load_rebate_data]
        
        # Create agent
        agent = AgentWorkflow.from_tools_or_functions(
            tools_or_functions=all_tools,
            llm=llm,
            verbose=True,
            system_prompt="""You are a helpful sales assistant with access to customer database and sales data.
            You can:
            - Retrieve customer information from the DB
            - Load discount and rebate CSV data
            - Combine them to provide insights to sales queries."""
        )
        logger.info("Agent initialized successfully")
        return agent
    except Exception as e:
        logger.error(f"Failed to initialize agent: {str(e)}")
        raise

# Initialize agent at startup
@app.on_event("startup")
async def startup_event():
    try:
        initialize_agent()
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise

@app.get("/")
async def root():
    return {
        "message": "Sales Agent API is running. Use /search endpoint to interact with the agent.",
        "endpoints": {
            "GET /search?q=your_search_term": "Search for information using the agent",
            "GET /docs": "Interactive API documentation"
        }
    }

@app.get("/search")
async def handle_query(search: str):
    if agent is None:
        raise HTTPException(
            status_code=500,
            detail="Agent is not properly initialized. Please check server logs."
        )
    
    try:
        if not search.strip():
            raise HTTPException(
                status_code=400,
                detail="Search query cannot be empty"
            )
            
        logger.info(f"Processing search query: {search}")
        
        # Process the query directly with the agent
        response = await agent.run(search)
        
        # Handle the response
        if hasattr(response, 'response'):
            response_text = str(response.response)
        else:
            response_text = str(response)
        
        # Clean up the response text
        response_text = response_text.replace('assistant:', '').strip()
        
        logger.info("Search completed successfully")
        return {"response": response_text}
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error processing search: {error_msg}")
        
        status_code = 500
        detail = f"Error processing your search: {error_msg}"
        
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
        "fastapi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )