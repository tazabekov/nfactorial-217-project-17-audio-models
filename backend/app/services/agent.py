"""The assistant's brain: a LangChain/LangGraph agent wired to MCP Playwright.

This is the backend's default wiring for Step 3 (see project README). The
teammate owning the agent/MCP work can extend ``VoiceAgent`` (e.g. add more
MCP servers, a custom prompt, or site-specific tools) without touching the
HTTP layer -- the orchestrator only calls ``VoiceAgent.ask``.

If MCP tools fail to load (e.g. Playwright MCP isn't installed locally yet),
the agent degrades gracefully to a plain LLM so the rest of the pipeline
(ASR -> agent -> TTS) still works end to end during development.
"""
import logging
from functools import lru_cache

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


class VoiceAgent:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._agent = None
        self._mcp_client = None

    def _build_llm(self):
        if self._settings.llm_provider == "anthropic":
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                model=self._settings.llm_model,
                api_key=self._settings.anthropic_api_key,
            )
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=self._settings.llm_model,
            api_key=self._settings.openai_api_key,
        )

    async def _load_mcp_tools(self) -> list:
        if not self._settings.mcp_enabled:
            return []
        try:
            from langchain_mcp_adapters.client import MultiServerMCPClient

            self._mcp_client = MultiServerMCPClient(
                {
                    "playwright": {
                        "command": self._settings.mcp_playwright_command,
                        "args": self._settings.mcp_playwright_args,
                        "transport": "stdio",
                    }
                }
            )
            return await self._mcp_client.get_tools()
        except Exception:
            logger.exception(
                "Failed to start/load the MCP Playwright server; "
                "falling back to a tool-less agent."
            )
            return []

    async def _ensure_agent(self):
        if self._agent is not None:
            return
        from langgraph.prebuilt import create_react_agent

        tools = await self._load_mcp_tools()
        llm = self._build_llm()
        self._agent = create_react_agent(
            llm, tools, prompt=self._settings.agent_system_prompt
        )

    async def ask(self, user_text: str, history: list[dict] | None = None) -> str:
        await self._ensure_agent()
        messages = [*(history or []), {"role": "user", "content": user_text}]
        result = await self._agent.ainvoke({"messages": messages})
        final_message = result["messages"][-1]
        content = final_message.content
        if isinstance(content, list):
            content = "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )
        return content.strip()

    async def aclose(self) -> None:
        close = getattr(self._mcp_client, "aclose", None) or getattr(
            self._mcp_client, "close", None
        )
        if close is not None:
            result = close()
            if hasattr(result, "__await__"):
                await result


@lru_cache
def get_voice_agent() -> VoiceAgent:
    return VoiceAgent(get_settings())
