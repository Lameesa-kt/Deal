"""
MCP Server for DealAgent
Exposes Sales Agent FastAPI endpoints as MCP tools

Installation:
    pip install mcp httpx

Run:
    python DealAgent/mcpserver.py
"""
import os
import httpx
from typing import Any

# Try to import FastMCP from MCP SDK
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    try:
        from mcp import FastMCP
    except ImportError:
        raise ImportError(
            "MCP SDK not found. Install with: pip install mcp\n"
            "Or try: pip install anthropic-mcp"
        )

# Sales Agent FastAPI URL
SALES_AGENT_URL = os.getenv("SALES_AGENT_API_URL", "http://127.0.0.1:8000")
# Deal Server URL
DEAL_SERVER_URL = os.getenv("DEAL_SERVER_URL", "http://127.0.0.1:3000")

# Initialize FastMCP server
mcp = FastMCP("DealAgentMCP")

@mcp.tool()
def query_sales_agent(query: str) -> dict[str, Any]:
    """
    Query the Sales Agent with a natural language question.
    
    This tool calls the Sales Agent's /query endpoint to get answers
    about customers, discounts, rebates, or any sales-related queries.
    
    Args:
        query: Natural language query (e.g., "Show me customer info for CompanyABC")
    
    Returns:
        Dictionary with response from the sales agent
        Example: {"response": "Customer ID: 1, Company: CompanyABC..."}
    """
    try:
        response = httpx.post(
            f"{SALES_AGENT_URL}/query",
            json={"query": query},
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        return {
            "status": "error",
            "response": f"HTTP {e.response.status_code}: {e.response.text}"
        }
    except httpx.RequestError as e:
        return {
            "status": "error",
            "response": f"Request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "response": f"Error: {str(e)}"
        }

@mcp.tool()
def get_deal_by_customer_id(customer_id: int) -> dict[str, Any]:
    """Get deal data by customer ID from Deal Server."""
    try:
        response = httpx.get(f"{DEAL_SERVER_URL}/api/getdeal/customer/{customer_id}", timeout=10.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"status": "error", "error": str(e), "customer_id": customer_id}

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()

