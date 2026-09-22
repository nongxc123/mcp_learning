from typing import Annotated
from pydantic import Field
from mcp.server.mcpserver import MCPServer, Context, Sample, Resolve
from mcp.types import SamplingMessage, TextContent, CreateMessageResult
from time import sleep


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

# 定义摘要生成 MCP 工具
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

# 定义网页搜索 MCP 工具
@mcp.tool(
    name="web-search",
    description="Search some web with a topic"
)
async def search(
    topic: str = Field(description="Topic to search"),
    *,
    context: Context
):
    # 发送处理日志
    # await context.info("Search......")
    # 发送进度信息
    await context.report_progress(20, 100)
    
    # 模拟网页搜索
    sleep(5)
    
    # await context.info("Writing report......")
    await context.report_progress(70, 100)
    
    # 模拟 AI 总结
    sleep(5)    
    
    return f"Topic: {topic}, web searching over"

