import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from .prompts import SYSTEM_PROMPT

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


async def get_agent_response(user_text: str) -> str:
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    mcp_config = {
        "playwright": {
            "command": "npx",
            "args": ["@playwright/mcp", "--headless"],
            "transport": "stdio",
        }
    }

    client = MultiServerMCPClient(mcp_config)

    async with client.session("playwright") as session:
        tools = await load_mcp_tools(session)

        agent = create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)

        result = await agent.ainvoke({"messages": [{"role": "user", "content": user_text}]})

    messages = result.get("messages", [])
    for message in reversed(messages):
        if hasattr(message, "content") and message.content:
            role = getattr(message, "type", "") or type(message).__name__
            if role in ("ai", "AIMessage"):
                return message.content

    return "Извините, не удалось найти информацию о событиях."
