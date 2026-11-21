from fastmcp import FastMCP

mcp = FastMCP("demo_server")

@mcp.tool()
def add(a: int, b: int) -> int:
    """加法工具，计算两个数字相加"""
    return a + b

if __name__ == "__main__":
    mcp.run()
