import os
import tempfile
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from llm import LLM

# 强制把路径切到你自己现在的代码文件夹
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

load_dotenv()

# 读取你的书
file_path = os.path.join(current_dir, "等级标准节选.txt")
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

docs = [Document(page_content=text)]
emb = OllamaEmbeddings(model="nomic-embed-text")
splits = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(docs)

print("正在建立向量数据库（使用临时安全路径）...")
# 【终极绝杀】用系统临时文件夹，绕开所有 Windows 权限和中文路径的坑！
temp_dir = tempfile.mkdtemp()
vs = Chroma.from_documents(documents=splits, embedding=emb, persist_directory=temp_dir)

retriever = vs.as_retriever(search_kwargs={"k": 2})
question = "HSK四级要求考生掌握多少个核心词汇？"
res = retriever.invoke(question)

print("\n✅ 成功检索到资料！")
print("--- 资料原文 ---")
print(res[0].page_content)

print("\n--- 交给 AI 生成答案 ---")
llm = LLM()
answer = llm.ask(f"根据以下资料回答问题：{question}\n资料：{res[0].page_content}", prefer="local")
print(answer)
