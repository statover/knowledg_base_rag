import sys
import os
# 自动计算：当前脚本往上一级，就是 knowledg_base_rag 项目根目录
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_path)

from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config import DEEPSEEK_API_KEY
from eval.test_cases import test_cases
from app.rag_agent import RAGAgent

def build_judge_chain():
    """构建评委大模型链，用来给回答的忠实度打分"""
    # 初始化评委模型，temperature=0保证打分稳定，不会随机
    judge_llm = ChatDeepSeek(model="deepseek-chat", api_key=DEEPSEEK_API_KEY, temperature=0)
    
    # 打分提示词：明确规则，让模型只输出数字分数
    judge_prompt = ChatPromptTemplate.from_template("""
    你是严谨的评测员。请根据【参考原文】判断【AI回答】是否完全基于原文，没有编造内容。
    
    评分规则：
    3分：完全基于原文，所有信息都能在原文中找到
    2分：大部分正确，存在少量原文没有的内容
    1分：大部分内容是编造的，和原文无关
    
    要求：只输出一个数字分数，不要任何解释、不要任何其他文字。
    
    参考原文：
    {context}
    
    AI回答：
    {answer}
    
    分数：
    """)

    #用LCEL串成链：提示词 -> 大模型 -> 解析字符串 -> 转成整数
    chain = (
        judge_prompt
        | judge_llm
        | StrOutputParser()
        | (lambda x: int(x.strip()))
    )
    return chain

def run_faithfulness_eval():
    """运行忠实度评测"""
    # 初始化RAG智能体
    rag = RAGAgent(init_file="data/test.txt")
    # 构建评委链
    judge_chain = build_judge_chain()

    total_score = 0
    total = len(test_cases)
    thread_id = "faith_eval_user"

    print("=" * 60)
    print("开始 RAG 忠实度评测")
    print(f"共 {total} 道测试题，满分3分")
    print("=" * 60)

    for i, case in enumerate(test_cases):
        question = case["question"]

        #1.拿到AI回答
        answer = rag.chat(question, thread_id=thread_id)

        #2.拿到检索到的原文
        context_docs = rag.retriever.invoke(question)
        # 把所有检索到的文档拼成一段字符串
        context = "\n\n".join(doc.page_content for doc in context_docs)

        # 3. 调用评委打分
        score = judge_chain.invoke({"context": context, "answer": answer})
        total_score += score

        print(f"\n[{i+1}/{total}] 得分：{score}/3")
        print(f"问题：{question}")
        print(f"回答：{answer[:60]}...")

    # 计算平均分
    avg_score = total_score / total
    print("\n" + "=" * 60)
    print("📊 忠实度评测结果")
    print(f"平均得分：{avg_score:.2f}/3")
    print("=" * 60)

    return {"avg_faithfulness": avg_score}

if __name__ == "__main__":
    run_faithfulness_eval()