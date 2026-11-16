import os
import csv
import sys
import ast
import json
import re
import operator
import datetime
import openai
from dotenv import load_dotenv

# 加载当前目录下的 .env 文件
load_dotenv()

# 直接在当前目录下找 生词表.csv（防止跨文件夹找不到）
current_dir = os.path.dirname(os.path.abspath(__file__))
VOCAB = os.path.join(current_dir, "生词表.csv")

# 默认使用智谱的 glm-4-flash 模型
MODEL = os.getenv("MODEL_NAME", "glm-4-flash")

_client = None

def get_client():
    global _client
    if _client is None:
        # 优先找 ZHIPU_API_KEY，找不到再找 DEEPSEEK_API_KEY
        key = os.getenv("ZHIPU_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
        if not key:
            raise RuntimeError("未配置 ZHIPU_API_KEY，请先在 .env 中填写")
        
        # 默认指向智谱的 API 地址
        base = os.getenv("BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")
        _client = openai.OpenAI(base_url=base, api_key=key)
    return _client

def get_time():
    return str(datetime.datetime.now())

# ---- 安全计算：白名单 AST，绝不使用裸 eval ----
_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}

def _eval_node(node):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("只允许数字与 + - * / ** % 运算")

def calc(expr):
    try:
        return str(_eval_node(ast.parse(str(expr), mode="eval")))
    except ZeroDivisionError:
        return "错误：除数为 0"
    except Exception as e:
        return "拒绝计算：%s" % e

def hsk_level(word):
    try:
        with open(VOCAB, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["词汇"].strip() == str(word).strip():
                    return "%s 是 %s 级" % (word, row["HSK等级"])
        return "未找到 %s" % word
    except FileNotFoundError:
        return "找不到 生词表.csv，请检查文件是否在同一文件夹下"

TOOLS = {"get_time": get_time, "calc": calc, "hsk_level": hsk_level}

SYS = ("你是国际中文助教。可用工具只有这 3 个：get_time（查当前时间，无参数）、"
       "calc（四则运算，如 calc('35*24')）、hsk_level（查生词 HSK 等级，如 hsk_level('把')）。"
       '如需调用，只输出一行 JSON，格式：{"tool": "工具名", "args": [参数]}；'
       "一次只调用一个工具，绝不编造不存在的工具名；无需工具时直接回答。")

def parse_calls(txt):
    s = (txt or "").strip()
    s = s.replace("```json", "").replace("```", "").strip()
    try:
        obj = json.loads(s)
        return [obj] if isinstance(obj, dict) else []
    except Exception:
        m = re.search(r"\{.*\}", s, re.S)
        if m:
            try:
                obj = json.loads(m.group())
                if isinstance(obj, dict):
                    return [obj]
            except Exception:
                pass
        calls = []
        for blk in re.findall(r"\{[^{}]*\}", s):
            try:
                obj = json.loads(blk)
            except Exception:
                continue
            if isinstance(obj, dict):
                calls.append(obj)
        return calls

def run(user_msg, max_calls=2):
    msgs = [{"role": "system", "content": SYS}, {"role": "user", "content": user_msg}]
    for _ in range(max_calls):
        txt = get_client().chat.completions.create(
            model=MODEL, messages=msgs).choices[0].message.content
        calls = [c for c in parse_calls(txt)
                 if isinstance(c.get("tool"), str) and c.get("tool") in TOOLS]
        if not calls:
            return txt
        results = []
        for call in calls:
            args = call.get("args") or []
            if not isinstance(args, list):
                results.append("工具参数格式错误：%r" % (args,))
                continue
            try:
                results.append("%s%r → %s" % (call["tool"], args, TOOLS[call["tool"]](*args)))
            except Exception as e:
                results.append("工具执行失败：%s" % e)
        msgs += [{"role": "assistant", "content": txt},
                 {"role": "user", "content": "工具返回：%s。请据此作答。" % "；".join(results)}]
    return get_client().chat.completions.create(
        model=MODEL, messages=msgs).choices[0].message.content

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "请依次查询两件事：1. '把'字的 HSK 等级是多少？2. 现在的时间是多少？"
    print("用户输入：", q)
    print("助手：", run(q))