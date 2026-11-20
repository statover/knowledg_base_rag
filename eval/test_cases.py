# 评测测试集：问题 + 正确答案关键词
test_cases = [
    {
        # 文档内题目：有明确答案
        "question": "RAG的全称是什么？",
        # 正确答案必须包含的关键词，命中一个就算对
        "answer_keywords": ["检索增强生成", "Retrieval-Augmented Generation"],
        # 题目类型：文档内/文档外
        "type": "in_doc"
    },
    {
        "question": "向量数据库的主要作用是什么？",
        "answer_keywords": ["存储向量", "相似度检索", "向量化匹配"],
        "type": "in_doc"
    },
    {
        "question": "Embedding是把什么转换成什么？",
        "answer_keywords": ["文本", "向量", "数字向量"],
        "type": "in_doc"
    },
    {
        "question": "文本切分为什么要设置重叠？",
        "answer_keywords": ["语义", "上下文", "切断", "连贯"],
        "type": "in_doc"
    },
    {
        "question": "Chroma和FAISS有什么区别？",
        "answer_keywords": ["持久化", "内存", "自动保存"],
        "type": "in_doc"
    },
    {
        "question": "RAG怎么降低大模型幻觉？",
        "answer_keywords": ["检索原文", "基于资料", "来源溯源"],
        "type": "in_doc"
    },
    {
        "question": "今天北京的天气怎么样？",
        "answer_keywords": ["没有相关信息", "暂无", "不知道", "无法回答"],
        "type": "out_doc"
    },
    {
        "question": "Python是谁发明的？",
        "answer_keywords": ["没有相关信息", "暂无", "不知道", "无法回答"],
        "type": "out_doc"
    },
    {
        "question": "RAG是谁提出的？",
        "answer_keywords": ["没有相关信息", "暂无", "不知道", "无法回答"],
        "type": "out_doc"
    },
    {
        "question": "芜湖今天会下雨吗？",
        "answer_keywords": ["没有相关信息", "暂无", "不知道", "无法回答"],
        "type": "out_doc"
    },
    # 自己再补充2道，一共10题，7道文档内+3道文档外
]
