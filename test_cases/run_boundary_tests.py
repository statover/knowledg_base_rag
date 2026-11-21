import sys
import os
import time

# 把项目根目录加入搜索路径，解决跨目录导入问题
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_path)

from app.rag_agent import RAGAgent
from app.utils import load_text_file
from app.logger import logger

# 测试用临时向量库目录，测试完可删除
TEST_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "test_chroma_db")
TEST_BASE_FILE = os.path.join(root_path, "data", "test.txt")
FILES_DIR = os.path.join(os.path.dirname(__file__), "files")

# 测试结果统计
pass_count = 0
total_count = 10

def print_result(case_id, case_name, is_pass, remark=""):
    global pass_count
    status = "✅ 通过" if is_pass else "❌ 失败"
    print(f"{case_id}. {case_name}：{status}")
    if remark:
        print(f"   备注：{remark}")
    if is_pass:
        pass_count += 1

def run_all_tests():
    print("="*50)
    print("RAG 系统边界测试开始")
    print("="*50)

    # 初始化测试用RAG智能体
    try:
        rag = RAGAgent(init_file=TEST_BASE_FILE)
        # 覆盖向量库路径，用测试独立库
        rag.vector_store = None
        from langchain_chroma import Chroma
        from app.embedding import embeddings
        from app.utils import split_documents
        docs = load_text_file(TEST_BASE_FILE)
        splits = split_documents(docs)
        rag.vector_store = Chroma.from_documents(
            splits, embeddings, persist_directory=TEST_PERSIST_DIR
        )
        rag.retriever = rag.vector_store.as_retriever(search_kwargs={"k": 3})
        rag._init_agent()
        print("ℹ️  测试环境初始化完成\n")
    except Exception as e:
        print(f"❌ 测试环境初始化失败：{e}")
        return

        # 1. 空文件上传
    case1 = os.path.join(FILES_DIR, "empty.txt")
    try:
        rag.add_file(case1)
        # 没有任何提示静默通过，属于防护不完善
        print_result(1, "空文件上传", False, "未拦截空文件，直接入库成功")
    except ValueError as e:
        # 主动抛出业务异常、返回友好提示，属于正常边界拦截，判定通过
        if "内容为空" in str(e) or "空" in str(e):
            print_result(1, "空文件上传", True, f"成功拦截，提示：{str(e)}")
        else:
            print_result(1, "空文件上传", False, f"其他值错误：{str(e)}")
    except Exception as e:
        # 非预期的异常崩溃，才算失败
        print_result(1, "空文件上传", False, f"意外报错：{str(e)}")


    # 2. 超大文件上传（12MB）
    case2 = os.path.join(FILES_DIR, "oversize_file.txt")
    file_size_mb = os.path.getsize(case2) / 1024 / 1024
    try:
        # 目前无大小校验会成功加入，有校验则会抛出异常
        rag.add_file(case2)
        print_result(2, "超大文件上传", False, f"文件大小{file_size_mb:.1f}MB，未被拦截")
    except Exception as e:
        print_result(2, "超大文件上传", True, f"成功拦截，提示：{str(e)}")

    # 3. 错误格式文件
    case3_list = [
        os.path.join(FILES_DIR, "fake_image.jpg"),
        os.path.join(FILES_DIR, "fake_doc.docx")
    ]
    pass_3 = True
    for f in case3_list:
        try:
            rag.add_file(f)
            pass_3 = False
            break
        except ValueError:
            continue
        except Exception:
            continue
    print_result(3, "错误格式文件", pass_3, "非TXT/PDF格式被拦截")

    # 4. 超长输入
    long_question = "测试超长输入" + "。重复填充内容" * 200
    try:
        answer = rag.chat(long_question)
        # 可优化为输入过长提示，当前不崩溃算基础通过
        if "过长" in answer or "太长" in answer:
            print_result(4, "超长输入", True, "成功返回输入过长提示")
        else:
            print_result(4, "超长输入", False, "未拦截超长输入，程序无崩溃")
    except Exception as e:
        print_result(4, "超长输入", False, f"报错：{str(e)}")

    # 5. 空输入
    try:
        answer = rag.chat("   ")
        if "有效问题" in answer or "输入" in answer:
            print_result(5, "空输入", True, f"返回提示：{answer}")
        else:
            print_result(5, "空输入", False, "未返回有效提示")
    except Exception as e:
        print_result(5, "空输入", False, f"报错：{str(e)}")

    # 6. GBK编码文件
    case6 = os.path.join(FILES_DIR, "gbk_encoding.txt")
    try:
        rag.add_file(case6)
        print_result(6, "乱码/GBK文件", False, "未做编码兜底，可能读取失败或乱码")
    except ValueError as e:
        # 业务层抛出的编码错误提示，符合预期
        if "编码不支持" in str(e):
            print_result(6, "乱码/GBK文件", True, "精准捕获编码错误并返回友好提示")
        else:
            print_result(6, "乱码/GBK文件", False, f"非预期错误：{str(e)}")
    except Exception as e:
        # 其他类型的异常都算不通过，说明我们的异常捕获不精准
        print_result(6, "乱码/GBK文件", False, f"非预期异常类型：{type(e).__name__}")

    # 7. 连续快速提问
    try:
        questions = ["RAG是什么？", "它有什么用？", "向量库是什么？", "怎么切分文档？", "Chroma和FAISS区别？"]
        for q in questions:
            rag.chat(q, thread_id="test_rapid")
            time.sleep(0.1)
        print_result(7, "连续快速提问", True, "5条连续提问全部正常响应")
    except Exception as e:
        print_result(7, "连续快速提问", False, f"报错：{str(e)}")

    # 8. 文档外问题
    try:
        answer = rag.chat("2026年世界杯冠军是谁？")
        if "暂无相关信息" in answer or "没有找到" in answer or "不知道" in answer:
            print_result(8, "文档外问题", True, "正确返回无相关信息")
        else:
            print_result(8, "文档外问题", False, "出现幻觉，回答了知识库外内容")
    except Exception as e:
        print_result(8, "文档外问题", False, f"报错：{str(e)}")

    # 9. 特殊字符输入
    special_q = "😀😁😂!@#$%^&*()_+ 这个符号是什么意思？"
    try:
        answer = rag.chat(special_q)
        # 不崩溃就算通过
        print_result(9, "特殊字符输入", True, "正常响应，无崩溃")
    except Exception as e:
        print_result(9, "特殊字符输入", False, f"报错：{str(e)}")

    # 10. 日志验证
    log_dir = os.path.join(root_path, "logs")
    today_log = os.path.join(log_dir, f"{time.strftime('%Y-%m-%d')}.log")
    if os.path.exists(today_log) and os.path.getsize(today_log) > 0:
        print_result(10, "日志验证", True, "当日日志文件存在且有记录")
    else:
        print_result(10, "日志验证", False, "未找到当日日志文件")

    # 汇总结果
    print("\n" + "="*50)
    print(f"测试完成：{pass_count} / {total_count} 通过")
    print("="*50)

if __name__ == "__main__":
    run_all_tests()
