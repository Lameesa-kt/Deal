# How to Run Deal Agent

The Deal Agent system consists of multiple components that need to be running in the correct order. Follow these steps to chat directly with DealAgent via API.

## Prerequisites

1. **Python 3.10+** installed
2. **Node.js** installed (for the Deal Server)
3. **Google API Key** (Gemini) - set as environment variable `GOOGLE_API_KEY`

## System Architecture

```
DealAgent API :8001
    ↓
    ├─→ Sales Agent API :8000 → Toolbox MCP :5001
    └─→ Deal Server (Node.js) :3000
```

## Step-by-Step Setup

### Step 1: Start Toolbox MCP Server (Port 5001)

This is required for the Sales Agent to access the database.

**PowerShell:**
```powershell
cd D:\ded\FinalDeal\sales_agent\database
$env:SQLITE_DATABASE = ".\customer.sqlite"
.\toolbox.exe --prebuilt sqlite --port 5001
```

**Keep this terminal running!** You should see output indicating the server is running on port 5001.

### Step 2: Start Sales Agent API (Port 8000)

Open a **NEW PowerShell terminal**:

```powershell
cd D:\ded\FinalDeal\sales_agent
$env:GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY"
python fastapi_server.py
```

Or if you prefer to set the environment variable permanently:
```powershell
$env:GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY"
python D:\ded\FinalDeal\sales_agent\fastapi_server.py
```

**Keep this terminal running!** The API should be available at `http://localhost:8000`

### Step 3: Start Deal Server (Node.js) (Port 3000)

Open a **NEW PowerShell terminal**:

```powershell
cd D:\ded\FinalDeal\DealAgent
npm install  # Only needed first time
node server.js
```

**Keep this terminal running!** The server should show: `Mock API running on port 3000`

### Step 4: Start DealAgent API (Port 8001)

Open a **NEW PowerShell terminal**:

```powershell
cd D:\ded\FinalDeal
$env:GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY"
python DealAgent\api.py
```

**Keep this terminal running!** The API should be available at `http://localhost:8001`

Now you can chat with DealAgent directly via the API (see "How to Chat with DealAgent" section below).

## Quick Start (All Commands)

If you want to run everything at once, here are all the commands in separate terminals:

**Terminal 1 - Toolbox:**
```powershell
cd D:\ded\FinalDeal\sales_agent\database
$env:SQLITE_DATABASE = ".\customer.sqlite"
.\toolbox.exe --prebuilt sqlite --port 5001
```

**Terminal 2 - Sales Agent:**
```powershell
cd D:\ded\FinalDeal\sales_agent
$env:GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY"
python fastapi_server.py
```

**Terminal 3 - Deal Server:**
```powershell
cd D:\ded\FinalDeal\DealAgent
node server.js
```

**Terminal 4 - DealAgent API:**
```powershell
cd D:\ded\FinalDeal
$env:GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY"
python DealAgent\api.py
```

Now you're ready to chat with DealAgent! See the "How to Chat with DealAgent" section below.

## Environment Variables

You can set these permanently for your user:

**PowerShell (permanent):**
```powershell
setx GOOGLE_API_KEY "YOUR_GEMINI_API_KEY"
setx MCP_PORT "5001"
setx SQLITE_DATABASE ".\customer.sqlite"
```

**Note:** After using `setx`, you need to open a new PowerShell window for the changes to take effect.

## Verification

1. **Check Toolbox:** Should be running on port 5001
2. **Check Sales Agent:** Visit `http://localhost:8000/` - should show API info
3. **Check Deal Server:** Visit `http://localhost:3000/api/getdeal/customer/1` - should return JSON
4. **Check DealAgent API:** Visit `http://localhost:8001/` - should show API info

## Troubleshooting

### Port Already in Use
If a port is already in use:
```powershell
# Find what's using the port
netstat -aon | findstr :8000

# Kill the process (replace PID with the number from above)
taskkill /PID <PID> /F
```

### Toolbox Not Found
If `toolbox.exe` is missing:
```powershell
cd D:\ded\FinalDeal\sales_agent\database
Invoke-WebRequest -Uri "https://storage.googleapis.com/genai-toolbox/v0.18.0/windows/amd64/toolbox.exe" -OutFile "toolbox.exe"
```

### Missing Dependencies
```powershell
# Install Python dependencies (if needed)
pip install fastapi uvicorn httpx google-adk

# Install Node.js dependencies
cd D:\ded\FinalDeal\DealAgent
npm install
```

## How to Chat with DealAgent

Once all services are running, you can interact with DealAgent via HTTP API calls. Here are several methods:

### Method 1: Using PowerShell (Invoke-RestMethod)

```powershell
# Send a query to DealAgent
$body = @{
    query = "Find CompanyABC's deal"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8001/query" -Method POST -Body $body -ContentType "application/json"
$response.response
```

### Method 2: Using curl (if available)

```powershell
curl -X POST http://localhost:8001/query -H "Content-Type: application/json" -d "{\"query\": \"Find CompanyABC's deal\"}"
```

### Method 3: Using Python

Create a simple Python script to chat with DealAgent:

```python
import httpx
import json

DEAL_AGENT_URL = "http://localhost:8001"

def chat_with_deal_agent(query):
    """Send a query to DealAgent and get response"""
    response = httpx.post(
        f"{DEAL_AGENT_URL}/query",
        json={"query": query},
        timeout=60.0
    )
    response.raise_for_status()
    result = response.json()
    return result["response"]

# Example usage
if __name__ == "__main__":
    while True:
        query = input("\nYou: ")
        if query.lower() in ['exit', 'quit', 'q']:
            break
        try:
            response = chat_with_deal_agent(query)
            print(f"DealAgent: {response}")
        except Exception as e:
            print(f"Error: {e}")
```

Save this as `chat.py` and run:
```powershell
python chat.py
```

### Method 4: Using Interactive Python

```powershell
python
```

Then in Python:
```python
import httpx

def ask(query):
    response = httpx.post("http://localhost:8001/query", json={"query": query})
    return response.json()["response"]

# Try it
print(ask("Find CompanyABC's deal"))
```

### Method 5: Using HTTP Client (Postman, Insomnia, etc.)

- **URL:** `http://localhost:8001/query`
- **Method:** POST
- **Headers:** `Content-Type: application/json`
- **Body:**
```json
{
  "query": "Find CompanyABC's deal"
}
```

## Example Queries

Try these queries with DealAgent:

- `"Find CompanyABC's deal"`
- `"Get deal information for customer ID 1"`
- `"Show me deal details for TechCorp Solutions"`
- `"What is the deal status for customer ID 2?"`
- `"Get customer ID for CompanyABC"`
- `"Show me the bid details for Global Logistics Inc"`

## How DealAgent Works

When you send a query, DealAgent will:
1. **Query the Sales Agent** to find customer IDs by company name
2. **Fetch deal data** from the Deal Server using the customer ID
3. **Return comprehensive deal information** including bid details, accounts, payment terms, etc.

## API Documentation

Once DealAgent API is running, visit `http://localhost:8001/docs` for interactive API documentation where you can test queries directly in your browser.

