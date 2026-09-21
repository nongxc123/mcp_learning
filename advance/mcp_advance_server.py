from typing import Annotated
from mcp.server.mcpserver import MCPServer, Context, Sample, Resolve
from mcp.types import SamplingMessage, TextContent, CreateMessageResult


mcp = MCPServer(name="advance_server", log_level="ERROR")

# Sampling 请求方法
def summarize_resolver(docs: list[str]) -> Sample:
    # 构建提示词
    prompt = f"""
Please summarize the following text:
{docs}
"""
    # 返回一个 Sampling 请求声明
    return Sample(
        # 插入提示词
        messages=[
            SamplingMessage(
                role="user",
                content=TextContent(type="text", text=prompt)
            )
        ],
        max_tokens=4096,
        system_prompt="You are a helpful research assistant."
    )    

# 定义 MCP 工具
@mcp.tool(
    name="summarize",
    description="Read the content of documents and summarize it"
)
def summarize(
    docs: list[str],
    # Sampling 参数注入
    summary: Annotated[CreateMessageResult, Resolve(summarize_resolver)]
):
    if summary.content.type == "text":
        return summary.content.text
    else:
        raise ValueError("Sampling failed")

    