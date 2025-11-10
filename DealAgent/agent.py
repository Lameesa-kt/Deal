import os
import httpx
from typing import Any, Dict

try:
    # Preferred in newer versions
    from google.adk import Agent  # type: ignore
except Exception:
    # Fallback for older package layouts
    from google.adk.agents import Agent  # type: ignore

# Sales Agent FastAPI URL
SALES_AGENT_URL = os.getenv("SALES_AGENT_API_URL", "http://127.0.0.1:8000")

# Deal Server URL (Node.js Express server)
DEAL_SERVER_URL = os.getenv("DEAL_SERVER_URL", "http://127.0.0.1:3000")


def query_sales_agent(query: str) -> Dict[str, Any]:
    """
    Query the Sales Agent with a natural language question.
    
    This tool calls the Sales Agent's FastAPI /query endpoint to get answers
    about customers, discounts, rebates, or any sales-related queries.
    
    Args:
        query: Natural language query (e.g., "Show me customer info for CompanyABC" or "Get customer ID for CompanyABC")
    
    Returns:
        Dictionary with response from the sales agent
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


def get_deal_by_customer_id(customer_id: int) -> Dict[str, Any]:
    """
    Get deal data by customer ID from the Deal Server.
    
    This tool calls the Deal Server's /api/getdeal/customer/:customer_id endpoint
    to retrieve deal information (bid details, accounts, terms, etc.) for a given customer.
    
    Args:
        customer_id: The customer ID (integer, e.g., 1, 2, 3)
    
    Returns:
        Dictionary with deal data including bidHead, bidAcct, etc.
    """
    try:
        response = httpx.get(
            f"{DEAL_SERVER_URL}/api/getdeal/customer/{customer_id}",
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        return {
            "status": "error",
            "error": f"HTTP {e.response.status_code}: {e.response.text}",
            "customer_id": customer_id
        }
    except httpx.RequestError as e:
        return {
            "status": "error",
            "error": f"Request failed: {str(e)}",
            "customer_id": customer_id
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error: {str(e)}",
            "customer_id": customer_id
        }


# Define the Agent explicitly as requested
agent = Agent(
    model="gemini-2.0-flash",
    name='Deal_agent',
    description="A simple deal agent with data and 1 database tool",
    instruction=
"""Your role:
- Identify the correct customer ID by company name using the customer server url from the sales agent.
- Use the matched customer’s ID to fetch the corresponding deal data (JSON).
- Return concise, accurate answers with supporting fields from the data. If something is missing or ambiguous, ask a brief clarifying question.
- Be helpful and friendly in your responses

Tools you can use:
1) Sales Agent Query Tool
   - query_sales_agent(query)
     Purpose: Query the Sales Agent FastAPI to get customer information, IDs, discounts, rebates, or any sales-related data.
     Required input: query (natural language string, e.g., "Get customer ID for CompanyABC" or "Show me customer info for CompanyABC")
     Output: Response from sales agent with customer data or answers

2) Deal Data (JSON source)
   - get_deal_by_customer_id(customer_id)
     Purpose: Fetch the deal JSON from Deal Server corresponding to the provided customer ID.
     Required input: customer_id (integer, e.g., 1, 2, 3)
     Output: Deal JSON with bidHead (bidNum, bidName, owner, dates, status, etc.) and bidAcct (account details, payment terms, etc.)

Decision & reasoning policy:
- Always first resolve the customer via query_sales_agent("Get customer ID for [company_name]").
- If multiple customers match, present a short disambiguation list (id + company_name) and ask the user to choose.
- Once a single customer is identified, call get_deal_by_customer_id with that customer’s id.
- Never fabricate IDs or deal details; only use tool outputs.
- If the user already supplies a customer_id, skip name lookup and go straight to fetching the deal.

Output format:
- Summarize the result briefly, then show key fields.
- If you used tools, reflect the final chosen customer and which deal was retrieved.
- If no results, say “No matching customer found” or “No deal found for this customer,” and suggest next steps.

Examples:
User: "Find CompanyABC's deal."
Assistant:
1) Call query_sales_agent("Get customer ID for CompanyABC")
2) Extract customer ID from the response
3) If multiple matches, ask user to pick an id; else:
4) Call get_deal_by_customer_id(<resolved_id>)
5) Return a concise summary + the key deal fields .
""",
    tools=[query_sales_agent, get_deal_by_customer_id]
)

# Expose a separate root_agent that points to the Agent instance
root_agent = agent
