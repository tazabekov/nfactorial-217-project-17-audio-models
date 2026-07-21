import asyncio
import sys
import os

sys.stdout.reconfigure(encoding="utf-8")
sys.stdin.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import get_agent_response


async def main():
    print("=== Voice Assistant Agent Test ===")
    print("Задавай вопросы про события в Алмате. Введи 'выход' для завершения.")
    print("=" * 40)

    while True:
        print()
        query = input("Твой вопрос: ").strip()
        if query.lower() in ("выход", "exit", "quit", "q"):
            print("Пока!")
            break
        if not query:
            continue

        print("Думаю...")
        response = await get_agent_response(query)
        print(f"\nОтвет: {response}")


if __name__ == "__main__":
    asyncio.run(main())
