
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek

load_dotenv()

llm = ChatDeepSeek(
    model="deepseek-flash",
    temperature=0.7,
    max_retries=2,
    timeout=30,
)

async def deepseek_invoke(messages: list[dict[str, str]]):
    response = llm.invoke(messages)
    return response