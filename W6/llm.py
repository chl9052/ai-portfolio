# W6 双引擎封装 —— 此后所有周统一经此调用
# 依赖：pip install openai requests python-dotenv
import os
import sys
import time

from dotenv import load_dotenv
load_dotenv()

import requests  # noqa: E402
import openai  # noqa: E402


class LocalEngine:
    """本地引擎（Ollama）：隐私任务优先、断网可用。"""

    def __init__(self, model=None):
        self.model = model or os.getenv("LOCAL_MODEL", "qwen2.5:0.5b")

    def ask(self, prompt, temperature=0.7, max_tokens=800):
        r = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "options": {"temperature": temperature, "num_predict": max_tokens},
                "stream": False,
            },
            timeout=60,
        )
        r.raise_for_status()
        return r.json()["message"]["content"]


class APIEngine:
    """云端引擎（智谱）：复杂任务、本地失败兜底。"""

    def __init__(self, base_url=None, model=None):
        self.base_url = base_url or "https://open.bigmodel.cn/api/paas/v4/"
        self.model = model or "glm-4-flash"
        self._client = None

    def _get_client(self):
        if self._client is None:
            key = os.getenv("ZHIPU_API_KEY") 
            if not key:
                raise RuntimeError(
                    "未配置 ZHIPU_API_KEY！请复制 .env.example 为 .env 并填入密钥。"
                )
            self._client = openai.OpenAI(base_url=self.base_url, api_key=key)
        return self._client

    def ask(self, prompt, temperature=0.7, max_tokens=800):
        r = self._get_client().chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        返回 r.choices[0].message.content


类 LLM：
    """统一入口：本地优先、云端兜底、双向异常自动切换。"""

    def __init__(self, local_model=None):
        self.local = LocalEngine(local_model)
        self.api = APIEngine()

    def ask(self, prompt, prefer="local", **kw):
        # 作业1：打印耗时。直观对比本地和云端的性能差异。
        开始时间 = time.time()
        
        如果 prefer == "local":
本地, 自我.api, "本地失败，自动切换云端"
        else:
            第一、第二、标签 = 自我.api, 自我.本地, "云端失败，自动切换本地"
            
        try:
            result = first.ask(prompt, **kw)
            print(f"⏱️ 本次调用耗时: {time.time() - start_time:.2f} 秒")
            返回结果
        except 异常 作为 e:
            print(f"[{tag}] {e}")
            result = second.ask(prompt, **kw)
            print(f"⏱️ 回退后总耗时: {time.time() - start_time:.2f} 秒")
            返回结果


如果 __name__ == "__main__":
    llm = LLM()
    
    打印("\n--- 测试1：正常本地 (带耗时) ---")
    #print(llm.ask("给《愚公移山》出一道 HSK4 阅读理解题", prefer="local"))
    
    # 如果你想测试第5组截断，就把下面这行的注释（#）去掉，跑一次
print("\n--- 测试4：云端失败自动回退 ---")
print(llm.ask("给《愚公移山》出一道 HSK4 阅读理解题", prefer="api"))
