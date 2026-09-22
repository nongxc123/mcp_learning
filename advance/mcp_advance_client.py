from contextlib import AsyncExitStack

from mcp import ClientSession, types
from mcp.client.streamable_http import streamable_http_client
from mcp.client.session import ClientRequestContext
from deepseek_client import deepseek_invoke

class MCPAdvanceClient:
    def __init__(self) -> None:
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()

    # Sampling 回调处理
    async def sampling_callback(
        self,
        context: ClientRequestContext,
        params: types.CreateMessageRequestParams
    ):
        # 消息列表
        messages = []
        # 解析 Sampling 消息
        for msg in params.messages:
            # 根据不同的角色分别解析
            if msg.role == "user" and msg.content.type == "text":
                content = (
                    msg.content.text
                    if hasattr(msg.content, "text")
                    else str(msg.content)
                )
                messages.append({
                    "role": "user",
                    "content": content
                })
            elif msg.role == "assistant" and msg.content.type == "text":
                content = (
                    msg.content.text
                    if hasattr(msg.content, "text")
                    else str(msg.content)
                )
                messages.append({
                    "role": "assistant",
                    "content": content
                })            
        # 调用 deepseek 接口
        response = await deepseek_invoke(messages)
        # 将调用结果返回
        return types.CreateMessageResult(
            role="assistant",
            content=types.TextContent(
                type="text",
                text=response.content
            ),
            model="deepseek-flash",
            stop_reason="endTurn"
        )
        
    # 进度信息回调处理
    async def print_progress_callback(
        self, progress: float, total: float | None, message: str | None
    ):
        if total is None:
            percentage = ( progress / total ) * 100
            print(f"Progress: { progress } / { total } ( { percentage:.1f} % )")
        else:
            print(f"Progress: { progress }")

    # 日志信息回调处理
    async def logging_callback(
        self, params: types.LoggingMessageNotificationParams
    ):
        print(f"[LOG][{params.level}] {params.data}")

    # 连接服务端
    async def connect(self, url: str):
        transport = await self.exit_stack.enter_async_context(
            streamable_http_client(url)
        )
        read, write = transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(
                read, 
                write, 
                # 记得在这里设置 sampling 回调！！！
                sampling_callback=self.sampling_callback,
                # 配置日志的回调处理
                logging_callback=self.logging_callback,
            )
        )
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

        return await self.session.call_tool(
            tool_name, 
            tool_input,
            # 配置进度的回调处理
            progress_callback=self.print_progress_callback
        )

    # 退出时关闭连接
    async def cleanup(self):
        await self.exit_stack.aclose()
