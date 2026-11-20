# 导入dotenv工具，用来读取.env文件
from dotenv import load_dotenv
# 导入os系统库，用来读取系统环境变量
import os

# 执行加载：读取项目根目录的.env文件，把变量注入到系统环境中
load_dotenv()

# 统一导出API密钥，所有文件都从这里导入
# 好处：以后换key只改这一个地方，不用到处找
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 向量库持久化路径，统一管理，不用每个文件写死路径
CHROMA_PERSIST_DIR = "./chroma_db"

# 默认文本切分参数
DEFAULT_CHUNK_SIZE = 200
DEFAULT_CHUNK_OVERLAP = 50

# 默认检索返回条数
DEFAULT_TOP_K = 3
