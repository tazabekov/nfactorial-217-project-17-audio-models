import asyncio
import sys
import os

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))

from agent import get_agent_response


async def main():
    queries = [
        "Что делать сегодня вечером в Алмате?",
        "Есть ли концерты или стендапы на этой неделе?",
        "What movies are playing in Almaty tonight?",
    ]

    for query in queries:
        print(f"\nЗапрос: {query}")
        print("-" * 60)
        response = await get_agent_response(query)
        print(f"Ответ: {response}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
