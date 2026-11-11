# 官方流水线与我的代码映射表
| 官方流水线 | llm-universe对应章节 | 我自己的代码 |
| :--- | :--- | :--- |
| Load + Split | C3 数据处理：读取、清洗与切片 | `open()` + `RecursiveCharacterTextSplitter(chunk_size=500, overlap=50)`，语料为HSK等级标准节选 |
| Embed + Store | C3 词向量及向量知识库 | `OllamaEmbeddings(model="nomic-embed-text")` + `Chroma` 本地持久化 |
| Retrieve | C4 基于LangChain搭建检索问答链 | `retrieve()` 函数取 top-2；`use_rag=True` 时先查资料再答 |
| Prompt + Generate | C4 将LLM接入LangChain | `build_prompt()` 拼 SYSTEM_PROMPT + 检索片段 + 问题，交 `LLM().ask()` |
| Deploy + Evaluate | C4 部署；C5 系统评估与优化 | W7 幻觉对照表是最朴素的评估；计划 W15 用 Streamlit 发布 |
