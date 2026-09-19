import asyncio

from mcp_simple_client import MCPSimpleClient


async def main():
    client = MCPSimpleClient()
    try:
        await client.connect("http://127.0.0.1:8000/mcp")
        print("连接成功！")

        # tools = await client.list_tools()
        # print("可用工具：")
        # for tool in tools:
        #     print(f"  - {tool.name}: {tool.description}")

        # # 测试调用 read_doc_contents
        # result = await client.call_tool("read_doc_contents", {"doc_id": "report.pdf"})
        # print("\n调用结果：")
        # print(result)

        resource = await client.read_resource("docs://documents")
        print("访问直接资源：")
        print(f"{resource}")

        t_resource = await client.read_resource("docs://documents/deposition.md")
        print("访问模板化资源 deposition.md ：")
        print(f"{t_resource}")

    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
