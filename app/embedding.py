# embedding.py —— 统一的本地向量化模块
from modelscope import snapshot_download
from langchain_huggingface import HuggingFaceEmbeddings

# 从魔搭下载模型（国内服务器快，已下载过会直接用缓存）
model_dir = snapshot_download("AI-ModelScope/bge-small-zh-v1.5")

# 用LangChain标准接口加载本地模型
embeddings = HuggingFaceEmbeddings(
    model_name=model_dir,           # 本地模型路径
    model_kwargs={"device": "cuda"}, # 用CPU，有GPU可以改"cuda"
    encode_kwargs={"normalize_embeddings": True}  # 归一化，余弦相似度更准
)
