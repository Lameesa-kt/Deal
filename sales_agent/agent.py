"""
Simple sales agent with LlamaIndex and Gemini
- Connects to Toolbox (SQLite) via MCP using toolbox-llamaindex minimal client
"""
import pandas as pd
import os
import asyncio
from llama_index.core import Settings
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core.agent.workflow import AgentWorkflow
# Toolbox MCP client (minimal usage per toolbox-llamaindex docs)
try:
    from toolbox_llamaindex import ToolboxClient  # https://github.com/googleapis/mcp-toolbox-sdk-python/tree/main/packages/toolbox-llamaindex#installation
except Exception:  # library not installed yet
    ToolboxClient = None

PORT = os.getenv("MCP_PORT", "5000")

# Function tools for CSV data loading
def load_discount_data():
    """Load discount.csv data and return summary information."""
    agent_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(agent_dir, 'data', 'discount.csv')
    df = pd.read_csv(csv_path)
    return {"status": "success", "message": f"Loaded {len(df)} discount tiers", "data": df.to_dict('records')}

def load_rebate_data():
    """Load rebate.csv data and return summary information."""
    agent_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(agent_dir, 'data', 'rebate.csv')
    df = pd.read_csv(csv_path)
    return {"status": "success", "message": f"Loaded {len(df)} rebate tiers", "data": df.to_dict('records')}

async def main():
    # Connect to Toolbox over MCP (no custom DB tools needed)
    if ToolboxClient is None:
        print("❌ toolbox-llamaindex is not installed. Run: pip install toolbox-llamaindex")
        return

    with ToolboxClient(f"http://127.0.0.1:{PORT}") as toolbox:
        tools = toolbox.load_toolset()
        # Combine CSV tools + Toolbox tool
        all_tools = tools + [load_discount_data, load_rebate_data]

        # Configure Gemini (require GOOGLE_API_KEY from environment; no hardcoded default)
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY is not set. Please set it in your environment.")
            return
        llm = GoogleGenAI(model="gemini-2.5-flash", api_key=api_key)
        Settings.llm = llm

        # Create the agent using LlamaIndex AgentWorkflow
        agent = AgentWorkflow.from_tools_or_functions(
            tools_or_functions=all_tools,
            llm=llm,
            verbose=True,
            system_prompt="""You are a helpful sales assistant with access to customer database and sales data.
            You can:
            - Retrieve customer information from the DB
            - Load discount and rebate CSV data
            - Combine them to provide insights to sales queries.
            
            IMPORTANT: When a user asks for customer information, details, or info about a company:
            - Use the get-customer-info tool to get FULL customer information (Customer_ID, Company_Name, Annual_Volume, Discount_Structure, Rebate_Structure)
            - Do NOT use get-customer-id unless the user specifically asks for just the ID number
            - Always present complete customer information including all fields when available."""
        )

        # Test the agent
        print("🤖 Sales Agent is ready! Ask me about customers, discounts, or rebates.")
        print("Example: 'Show me customer info for CompanyABC' or 'What are the discount tiers?'")
        
        # Interactive loop
        while True:
            try:
                user_input = input("\n👤 You: ")
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                response = await agent.run(user_input)
                print(f"🤖 Agent: {response}")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())