from typing import Annotated
from pydantic import Field
from mcp.server.mcpserver import MCPServer, Context, Sample, Resolve, ListRoots
from mcp.types import SamplingMessage, TextContent, CreateMessageResult, ListRootsResult
from time import sleep
from utils import file_url_to_path
from pathlib import Path
import asyncio

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
    await asyncio.sleep(5)
    
    # await context.info("Writing report......")
    await context.report_progress(70, 100)
    
    # 模拟 AI 总结
    await asyncio.sleep(5) 
    
    return f"Topic: {topic}, web searching over"

# 定义一个解析器，返回 ListRoots() 标记
def get_workspace_roots() -> ListRoots:
    return ListRoots()

# 定义获取 Roots 的工具
@mcp.tool(
    name="root-list",
    description="Get roots list"
)
async def list_roots(
    roots: Annotated[ListRootsResult, Resolve(get_workspace_roots)]
) -> list[str]:
    client_roots = roots.roots
    
    # 通过 Root 对象中的 uri，将 uri 转化为 Path 对象
    return [str(file_url_to_path(root.uri)) for root in client_roots]

# 确认请求的路径是否允许访问，是否在 roots 中
def is_path_allowed(
    requested_path: Path,
    roots: ListRootsResult,
) -> bool:
    if not requested_path.exists():
        return False
    if requested_path.is_file():
        requested_path = requested_path.parent
        
    for root in roots.roots:
        root_path = file_url_to_path(root.uri)
        try:
            requested_path.relative_to(root_path)
            return True
        except ValueError:
            continue
        
    return False

# 读取文件工具
@mcp.tool(
    name="read-file",
    description="Read a file"
)
async def read_file(
    path: str,
    roots: Annotated[ListRootsResult, Resolve(get_workspace_roots)]
) -> str:
    requested_path = Path(path).resolve()
    
    if not is_path_allowed(requested_path, roots):
        return f"拒绝访问：{path.split("/")[-1]}，因为不在允许的根目录范围内"
    
    return f"允许访问"