## Setup: MCP Toolbox (SQLite) + LlamaIndex Agent on Windows

References: SQLite using MCP (Toolbox): https://googleapis.github.io/genai-toolbox/how-to/connect-ide/sqlite_mcp/

-- toolbox-llamaindex install/usage: https://github.com/googleapis/mcp-toolbox-sdk-python/tree/main/packages/toolbox-llamaindex#installation

### 0) Prerequisites
- Windows PowerShell or Git Bash
- Python 3.10+
- Project at `D:\ded\Final`

### Known working quickstart (from your history)
PowerShell:
```powershell
cd D:\ded\Final\sales_agent\database
Invoke-WebRequest -Uri "https://storage.googleapis.com/genai-toolbox/v0.18.0/windows/amd64/toolbox.exe" -OutFile "toolbox.exe"
pip install -r requirements.txt
pip install pandas
pip install llama-index-core llama-index-llms-google-genai
$env:SQLITE_DATABASE = ".\customer.sqlite"
./toolbox.exe --prebuilt sqlite --port 5001
```
New PowerShell for the agent:
```powershell
cd D:\ded\Final\sales_agent
$env:MCP_PORT = "5001"
$env:GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY"
python agent.py
```

### 1) Download Toolbox (Windows)
Run in PowerShell from `D:\ded\Final\sales_agent\database`:
```powershell
Invoke-WebRequest -Uri "https://storage.googleapis.com/genai-toolbox/v0.18.0/windows/amd64/toolbox.exe" -OutFile "toolbox.exe"
.\toolbox.exe --version
```

### 2) Install Python dependencies
```powershell
pip install -r D:\ded\Final\sales_agent\database\requirements.txt
pip install pandas
pip install llama-index-core llama-index-llms-google-genai
```

### 3) Start Toolbox (pick a free port)
Run ONE of the following in `D:\ded\Final\sales_agent\database`:

Option A — Prebuilt SQLite (no YAML needed)
```powershell
cd D:\ded\Final\sales_agent\database
$env:SQLITE_DATABASE = ".\customer.sqlite"
.\toolbox.exe --prebuilt sqlite --port 5001
```

Option B — With `tools.yaml`
```powershell
cd D:\ded\Final\sales_agent\database
.\toolbox.exe --tools-file tools.yaml --port 5001
```

Keep this terminal running.

Notes:
- Do not chain commands with `&&` in PowerShell; run them on separate lines.
- If port 5000 is busy (“Hello World” or bind error), use 5001 and keep using it consistently.

### 4) Run the agent on the same port
Open a NEW terminal:
```powershell
set MCP_PORT=5001
set GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
python D:\ded\Final\sales_agent\agent.py
```

### 5) Use the agent
- Example prompt: “Find customers with Tech in the company name”.
- The agent loads Toolbox tools via `ToolboxClient(...).load_toolset()` and adds your CSV tools.

### 6) Port troubleshooting
Check what’s listening:
```powershell
netstat -aon | findstr :5000
netstat -aon | findstr :5001
```
Stop the conflicting process:
```powershell
tasklist /FI "PID eq <PID>"
taskkill /PID <PID> /F
```

### 7) Environment variables quick reference
PowerShell (current session):
```powershell
$env:MCP_PORT = "5001"
$env:SQLITE_DATABASE = ".\customer.sqlite"
$env:GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY"
```
Persist for future shells:
```powershell
setx MCP_PORT "5001"
setx GOOGLE_API_KEY "YOUR_GEMINI_API_KEY"
# open a new PowerShell to take effect
```

### Do I need to install SQLite separately?
- No. SQLite is embedded; Toolbox reads the `.sqlite` file directly.
- Python ships with the `sqlite3` module; no extra install is required.

### 8) Git: exclude toolbox.exe (large binary)
Do not commit `toolbox.exe` (~150 MB). If already committed:
```powershell
git rm --cached sales_agent/database/toolbox.exe
echo sales_agent/database/toolbox.exe >> .gitignore
git add .gitignore
git commit -m "Stop tracking toolbox.exe"
pip install git-filter-repo
git filter-repo --invert-paths --path sales_agent/database/toolbox.exe
git push --force origin master
```

### 9) Git Bash equivalents
Start Toolbox:
```bash
cd /d/ded/Final/sales_agent/database
export SQLITE_DATABASE=./customer.sqlite
./toolbox.exe --prebuilt sqlite --port 5001
# or: ./toolbox.exe --tools-file tools.yaml --port 5001
```
Run agent:
```bash
export MCP_PORT=5001
export GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
python /d/ded/Final/sales_agent/agent.py
```


