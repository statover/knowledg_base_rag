import sys
import os
# 自动计算：当前脚本往上一级，就是 knowledg_base_rag 项目根目录
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_path)

import time
from eval.test_cases import test_cases
from app.rag_agent import RAGAgent

def run_accuracy_eval():
    """运行准确率和延迟评测"""
    rag = RAGAgent(init_file="data/test.txt")
    #会话ID固定，评测用同一个会话
    thread_id = "eval_user"

    #统计变量：正确题数、总耗时
    correct_count = 0
    total_time = 0
    total = len(test_cases)

    print("=" * 60)
    print("开始 RAG 准确率和延迟评测")
    print(f"共 {total} 道测试题")
    print("=" * 60)

    for i, case in enumerate(test_cases):
        question = case["question"]
        keywords = case["answer_keywords"]

        #记录开始时间
        start_time = time.time()
        #调用智能体获取问答
        answer = rag.chat(question, thread_id=thread_id)
        #计算耗时
        cost_time = time.time() - start_time
        total_time += cost_time

        # 判断是否正确：答案里包含任意一个关键词就算正确
        # 把答案和关键词都转小写，避免大小写影响
        is_correct = any(kw.lower() in answer.lower() for kw in keywords)
        if is_correct:
            correct_count += 1
            status = "正确"
        else:
            status = "错误"

        # 打印每道题的结果
        print(f"\n[{i+1}/{total}] {status} | 耗时 {cost_time:.2f}s")
        print(f"问题：{question}")
        print(f"回答：{answer[:80]}...")
        print(f"关键词：{keywords}")

    # 计算最终指标
    accuracy = correct_count / total * 100
    avg_latency = total_time / total

    print("\n" + "=" * 60)
    print("📊 评测结果")
    print(f"准确率：{accuracy:.1f}% ({correct_count}/{total})")
    print(f"平均延迟：{avg_latency:.2f} 秒")
    print("=" * 60)

    # 返回结果，后面生成报告用
    return {
        "accuracy": accuracy,
        "avg_latency": avg_latency,
        "total_cases": total,
        "correct_count": correct_count
    }

# 直接运行这个文件就执行评测
if __name__ == "__main__":
    run_accuracy_eval()