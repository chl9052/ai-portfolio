@mcp.tool()
def hsk_level(word: str) -> str:
    """查询某个词属于 HSK 几级。"""
    for row in _rows():
        if row["词汇"].strip() == str(word).strip():
            return "%s -> %s 级" % (word, row["HSK等级"])
    return "未找到 %s" % word


@mcp.tool()
def list_by_level(level: str) -> str:
    """列出某一 HSK 等级的全部词汇。"""
    out = [row["词汇"] for row in _rows() if row["HSK等级"] == str(level).strip()]
    return "、".join(out) if out else "该等级暂无词汇"


# ============在这里粘贴新增的count_by_level工具===========
@mcp.tool()
def count_by_level(level: str) -> str:
    """统计指定HSK等级的词汇总数量。"""
    words = [row["词汇"] for row in _rows() if row["HSK等级"] == str(level).strip()]
    return f"HSK {level} 级词汇数量：{len(words)}"
# ======================================================


if __name__ == "__main__":
    mcp.run()
