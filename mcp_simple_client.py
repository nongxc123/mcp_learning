import json
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession, types
from mcp.client.streamable_http import streamable_http_client


class MCPSimpleClient:
    def __init__(self) -> None:
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()

    # 连接服务端
    async def connect(self, url: str):
        # 建立 HTTP 连接，并把断开连接的动作交给 exit_stack 托管
        transport = await self.exit_stack.enter_async_context(
            # http 连接客户端，url 是服务端地址
            streamable_http_client(url)
        )
        # 取出读写通道
        read, write = transport
        # 建立 MCP 会话，交给 exit_stack 管理
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        # 协议握手
        await self.session.initialize()

    # 获取服务端工具列表
    async def list_tools(self) -> list[types.Tool]:
        if self.session is None:
            return []

        result = await self.session.list_tools()
        return result.tools

    # 请求服务端执行工具
    async def call_tool(
        self, tool_name: str, tool_input: dict
    ) -> types.CallToolResult | None:
        if self.session is None:
            return None

        return await self.session.call_tool(tool_name, tool_input)

    # 读取资源
    async def read_resource(self, uri: str) -> Any:
        if self.session is None:
            return None
        result = await self.session.read_resource(uri)
        resource = result.contents[0]

        if isinstance(resource, types.TextResourceContents):
            if resource.mime_type == "application/json":
                return json.loads(resource.text)
            elif resource.mime_type == "text/plain":
                return resource.text
        return None

    # 退出时关闭连接
    async def cleanup(self):
        await self.exit_stack.aclose()
