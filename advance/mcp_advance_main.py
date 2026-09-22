import asyncio

from mcp_advance_client import MCPAdvanceClient

# 自定义文档，模拟网页检索结果
docs = [
    "人工智能自二十世纪五十年代提出以来，经历多次起伏，逐步从理论探索走向实际应用。",
    "深度学习在图像识别、语音处理等领域取得突破，推动人工智能进入快速发展阶段。",
    "大语言模型凭借海量数据和强大算力，能够生成文本、编写代码并辅助复杂决策。",
    "人工智能正融入医疗、教育、金融和制造等行业，提升效率并催生新的商业模式。",
    "未来人工智能需兼顾创新与安全，完善伦理规范和法律监管，才能实现可持续发展。",
]

async def main():
    client = MCPAdvanceClient()
    try:
        await client.connect("http://127.0.0.1:8000/mcp")
        print("连接成功！")

        # tools = await client.list_tools()
        # print("可用工具：")
        # for tool in tools:
        #     print(f"  - {tool.name}: {tool.description}")

        # result = await client.call_tool("summarize", {"docs": docs})
        # print("\n调用结果：")
        # print(result.content[0].text)    

        result = await client.call_tool("web-search", {"topic": "Claude Academy"})
        print("\n调用结果：")
        print(result.content[0].text)             

    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
