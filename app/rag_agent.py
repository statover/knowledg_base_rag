# 导入新版标准Agent创建入口
from langchain.agents import create_agent
# 导入DeepSeek大模型客户端
from langchain_deepseek import ChatDeepSeek
# 导入工具装饰器
from langchain_core.tools import tool
# 导入内存记忆检查点，实现多轮对话记忆
from langgraph.checkpoint.memory import InMemorySaver
# 导入Chroma向量库（官方独立维护）
from langchain_chroma import Chroma
# 导入统一配置
from app.config import DEEPSEEK_API_KEY, CHROMA_PERSIST_DIR, DEFAULT_TOP_K
# 导入工具函数
from app.utils import split_documents, load_text_file
# 导入本地向量化模型
from app.embedding import embeddings
#顶部导入统一日志器
from app.logger import logger


class RAGAgent:
    def __init__(self, init_file: str = None):
        """初始化RAG智能体
        传init_file就加载初始文档建新库；不传就加载已有的持久化库
        """
        if init_file:
            # 加载初始文档
            docs = load_text_file(init_file)
            # 切分文档
            splits = split_documents(docs)
            # 创建Chroma向量库，自动持久化到本地文件夹
            self.vector_store = Chroma.from_documents(
                splits,
                embeddings,
                persist_directory=CHROMA_PERSIST_DIR
            )
        else:
            # 直接加载已有的持久化向量库
            self.vector_store = Chroma(
                persist_directory=CHROMA_PERSIST_DIR,
                embedding_function=embeddings
            )
        # 转成标准检索器
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": DEFAULT_TOP_K})

        logger.info(f"向量库初始化完成，共{len(splits) if init_file else '已加载持久化库'} 条文档片段")
        # 初始化Agent
        self._init_agent()

    def add_texts(self, texts: list[str]):
        """增量新增纯文本到知识库，无需重建全库"""
        from langchain_core.documents import Document
        # 批量包装成Document对象
        new_docs = [Document(page_content=t) for t in texts]
        # 统一切分
        new_splits = split_documents(new_docs)
        # 添加到向量库，自动持久化
        self.vector_store.add_documents(new_splits)
        # 增量新增文档完成日志
        logger.info(f"增量新增文档完成，新增 {len(new_splits)} 条片段")

    def add_file(self, file_path: str):
        """新增文件到知识库，自动判断TXT/PDF格式"""
        if file_path.endswith(".txt"):
            docs = load_text_file(file_path)
        elif file_path.endswith(".pdf"):
            from app.utils import load_pdf_file
            docs = load_pdf_file(file_path)
        else:
            raise ValueError("仅支持TXT和PDF格式")

        if not docs or all(not doc.page_content.strip() for doc in docs):
            logger.warning(f"文件内容为空，跳过入库：{file_path}")
            raise ValueError("文件内容为空，无法加载到知识库")
        
        splits = split_documents(docs)
        self.vector_store.add_documents(splits)

    def _init_agent(self):
        """初始化带工具和记忆的Agent"""
        @tool
        def search_knowledge(query: str) -> str:
            """从知识库检索相关文档内容"""
            try:
                # 空查询直接返回提示
                if not query.strip():
                    return "查询内容不能为空"

                #执行检索查询日志（DEBUG级）
                logger.debug(f"执行检索查询：{query.strip()}")
                # 调用检索器查找相关片段
                docs = self.retriever.invoke(query.strip())
                #检索结果数量日志（DEBUG级）
                logger.debug(f"检索到 {len(docs)} 条相关结果")
                # 无匹配结果返回提示
                if not docs:
                    return "知识库中没有找到相关内容"
                # 拼接所有检索结果并返回
                return "\n\n".join(f"[片段{i+1}]\n{d.page_content}" for i, d in enumerate(docs))
            except Exception as e:
                # 异常兜底，返回友好提示，程序不崩溃
                return f"检索出错：{str(e)}"

            

        

        # 初始化大模型
        llm = ChatDeepSeek(model="deepseek-chat", api_key=DEEPSEEK_API_KEY)
        # 创建记忆存储器
        self.checkpointer = InMemorySaver()
        # 创建完整Agent
        self.agent = create_agent(
            model=llm,
            tools=[search_knowledge],
            system_prompt="""你是专业的知识库问答助手。
            1. 回答必须完全基于检索到的文档资料，资料中没有的就是明确说：知识库中暂无相关信息
            2. 回答分点表述，清晰易懂
            3. 结合对话上下文理解用户问题，处理指代、追问
            4. 语言简洁，不罗嗦
            5. 严禁编造任何原文没有的信息""", 
            checkpointer=self.checkpointer
        )

    def chat(self, user_input: str, thread_id: str = "default") -> str:
        """对外公开的安全对话接口，带异常兜底"""
        try:
            # 1. 输入长度校验，防止超长输入导致异常
            if len(user_input) > 1000:
                logger.warning(f"用户输入过长，长度：{len(user_input)}")
                return "输入内容太长了，请精简后再提问（最多1000字）"
            # 2. 空输入校验
            if not user_input.strip():
                return "请输入有效问题"
            # 会话配置，thread_id区分不同对话，绑定对应记忆
            config = {"configurable": {"thread_id": thread_id}}
            logger.info(f"用户提问：{user_input[:50]}... | 会话ID：{thread_id}")

            # 调用Agent，内部自动判断是否调用检索工具
            result = self.agent.invoke(
                {"messages": [("user", user_input)]},
                config=config
            )

            answer = result["messages"][-1].content
            logger.info(f"回答完成，长度：{len(answer)}")
            # 返回AI最终回答
            return answer
        
        except Exception as e:
            #对话异常错误日志
            logger.error(f"对话异常：{str(e)}", exc_info=True)
            return f"服务暂时不可用,请稍后再试"
