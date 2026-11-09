# 官方 RAG 流水线映射表

| 官方流水线 | 我的 rag_qa.py 对应代码 |
| :--- | :--- |
| Load + Split 加载与分块 | `open()` 读取 + `RecursiveCharacterTextSplitter(500/50)` |
| Embed + Store 向量化入库 | `OllamaEmbeddings(nomic-embed-text)` + `Chroma` |
| Retrieve 检索 | `retrieve()` 取 top-2 |
| Prompt + Generate 拼词与生成 | `build_prompt()` 拼系统词与问题，交 `llm.ask()` |
| Deploy + Evaluate 部署与评估 | 通过 `assistant_v1.py` 集成演示；用幻觉对照表评估 |