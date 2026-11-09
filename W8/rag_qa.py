import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "等级标准节选.txt")
emb = OllamaEmbeddings(model="nomic-embed-text")

_vs = None
_retriever = None

def get_retriever():
    global _vs, _retriever
    if _retriever is None:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        docs = [Document(page_content=text, metadata={"source": "等级标准节选.txt"})]
        splits = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(docs)
        _vs = Chroma.from_documents(documents=splits, embedding=emb)
        _retriever = _vs.as_retriever(search_kwargs={"k": 2})
    return _retriever

# 老师要的 retrieve 函数
def retrieve(question):
    retriever = get_retriever()
    return retriever.invoke(question)

# 老师要的 build_prompt 函数
def build_prompt(question, docs):
    context = "\n\n".join([d.page_content for d in docs])
    prompt = f"""你是一个严谨的学科助手。请根据以下提供的资料回答问题。
如果资料中找不到答案，请如实说“资料中未提及”，不要自己编造。
问题：{question}
资料：{context}
"""
    return prompt