import os
from app.logger import logger
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from app.config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP


def load_text_file(file_path: str) -> list[Document]:
    """加载TXT文件，返回Document对象列表"""
    try:
        #先判断文件是否存在
        if not os.path.exists(file_path):
            logger.warning(f"文件不存在：{file_path}")
            raise FileNotFoundError("文件不存在")
        
    # 以只读模式打开文件，指定utf-8防止中文乱码
        with open(file_path, "r", encoding="utf-8") as f:
        # 读取文件全部内容
             content = f.read()

        if not content.strip():
           logger.warning(f"文件内容为空：{file_path}")
           raise ValueError("文件内容为空")

        logger.info(f"TXT文件加载成功：{file_path}")
        # 包装成标准Document，加上来源元数据
        return [Document(page_content=content, metadata={"source": file_path})]

    except UnboundLocalError:
        #编码错误单独捕获，给用户明确提示
        logger.error(f"文件编码错误：{file_path}")
        raise ValueError("文件编码不支持，请使用UTF-8编码的TXT文件")
    except Exception as e:
        logger.error(f"TXT文件加载失败：{str(e)}", exc_info=True)
        raise


def load_pdf_file(file_path: str) -> list[Document]:
    """加载PDF文件，每页返回一个Document"""
    # 创建PDF读取器对象
    reader = PdfReader(file_path)
    docs = []
    # 遍历PDF每一页
    for i, page in enumerate(reader.pages):
        # 提取当前页的纯文本
        text = page.extract_text()
        # 非空页面才加入列表，跳过空白页
        if text.strip():
            docs.append(Document(
                page_content=text,
                metadata={"source": file_path, "page": i + 1}
            ))
    return docs


def split_documents(docs: list[Document]) -> list[Document]:
    """统一的文档切分函数，全项目共用一套参数"""
    # 创建切分器，用配置里的默认大小和重叠值
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=DEFAULT_CHUNK_SIZE,
        chunk_overlap=DEFAULT_CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""]
    )
    # 执行切分并返回结果
    return text_splitter.split_documents(docs)
