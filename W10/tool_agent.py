import asyncio
import json
from openai import OpenAI
from fastmcp import Client

# 智谱大模型配置
llm = OpenAI(
    api_key="在这里填入你的密钥",
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

async def main():
    # Client直接加载server文件，官方写法，不会报StreamReader错误
    async with Client("server.py") as client:
        # 获取MCP里的工具列表
        tools = await client.list_tools()
        tool_defs = []
        for t in tools:
            tool_defs.append({
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.inputSchema
                }
            })

        # 发给大模型
        resp = llm.chat.completions.create(
            model="glm-4-flash",
            messages=[{"role": "user", "content":"帮我算 12 + 34"}],
            tools=tool_defs,
            tool_choice="auto"
        )

        msg = resp.choices[0].message
        if msg.tool_calls:
            call = msg.tool_calls[0]
            args = json.loads(call.function.arguments)
            result = await client.call_tool(call.function.name, args)
            print("✅ 计算结果：", result.data)

if __name__ == "__main__":
    asyncio.run(main())
