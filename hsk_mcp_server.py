from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hsk")

hsk_data = {
    "1": ["你", "好", "我", "是"],
    "2": ["爸爸", "妈妈", "朋友"],
    "3": ["把", "看", "听", "走"]
}

@mcp.tool()
def hsk_level(word: str) -> str:
    """查询词语所属HSK等级"""
    for level, words in hsk_data.items():
        if word in words:
            return f"{word} -> HSK{level}"
    return f"{word} 不在HSK词表中"

@mcp.tool()
def list_by_level(level: str) -> list[str]:
    """按等级列出该等级全部词汇"""
    return hsk_data.get(level, [])

@mcp.tool()
def count_by_level(level: str) -> int:
    """统计该等级词汇数量"""
    return len(hsk_data.get(level, []))

if __name__ == "__main__":
    mcp.run()
