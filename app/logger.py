# 导入Python标准库的日志模块，不用额外安装
import logging
# 导入os系统库，用来创建日志文件夹
import os
# 导入时间模块，用来给日志文件按日期命名
from datetime import datetime

def get_logger(name: str = "rag_project") -> logging.Logger:
    """
    获取统一配置的日志器
    参数name：日志器的名字，一般传模块名，方便区分是哪个模块打的日志
    """
    # 创建日志文件夹，如果不存在就自动建
    log_dir = "./logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 生成日志文件名，按当天日期命名，每天一个日志文件
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = f"{log_dir}/{today}.log"

    # 获取日志器对象
    logger = logging.getLogger(name)
    
    # 防止重复添加处理器，导致同一条日志打印多次
    if logger.handlers:
        return logger

    # 设置日志最低级别：DEBUG及以上的日志都会被记录
    # 级别从低到高：DEBUG < INFO < WARNING < ERROR < CRITICAL
    logger.setLevel(logging.DEBUG)

    # ========== 定义日志格式 ==========
    # 格式：时间 - 日志级别 - 日志器名字 - 日志内容
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # ========== 处理器1：输出到控制台（终端）==========
    console_handler = logging.StreamHandler()
    # 控制台只显示INFO及以上级别，DEBUG调试信息不刷屏
    console_handler.setLevel(logging.INFO)
    # 应用上面定义的格式 【修正点：这里是 setFormatter，不是 setLevel】
    console_handler.setFormatter(formatter)

    # ========== 处理器2：输出到文件（持久化保存）==========
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    # 文件里记录所有级别，包括DEBUG，方便排查问题
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # 把两个处理器加到日志器上
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# 导出一个默认的全局日志器，简单场景直接导入用
logger = get_logger()
