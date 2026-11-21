import gradio as gr
import os
import uuid
from app.config import CHROMA_PERSIST_DIR
from app.rag_agent import RAGAgent
from app.logger import logger

#全局初始化智能体
if os.path.exists(CHROMA_PERSIST_DIR):
    logger.info("检测到已有向量库，直接加载")
    rag_agent = RAGAgent()
else:
    logger.info("首次运行，初始化示例知识库")
    rag_agent = RAGAgent(init_file="data/test.txt")


#处理文件上传
def upload_document(file_path):
    """用户上传之后、自动切分、向量化、加入知识库"""
    try:
        # 1. 判断文件大小，限制最大10MB，防止超大文件拖垮服务
        file_size = os.path.getsize(file_path) / 1024 /1024
        if file_size > 10:
            logger.warning(f"上传文件过大：{file_size:.2f}MB")
            return "文件太大了，最大支持10MB"
        
        #直接调用Agent里封装好多add_file方法
        rag_agent.add_file(file_path)
        logger.info(f"文件上传成功：{file_path}")
        return "上传成功！文档已经加入知识库，可以开始提问了"

    except Exception as e:
        logger.error(f"文件上传失败：{str(e)}", exc_info=True)
        return"上传失败，请检查文件格式后重试"

#处理聊天回复
#参数message：用户刚输入的最新一条消息
#参数history：聊天框里全部历史记录，格式是字典列表
def chat_respond(message, history, session_id):
    """用户发消息后，调用Agent拿到回答，更新来聊天界面"""
    #调用RAG智能体的chat方法，传入问题和会话ID
    #thread_id固定为web_user，同为一个网页窗口共享记忆
    bot_answer = rag_agent.chat(message, thread_id=session_id)
    #把用户说的话追加到聊天记录里去
    history.append({"role": "user", "content": message})
    #把AI的回答追加到聊天历史里
    history.append({"role": "assistant", "content": bot_answer})
    #空字符串：用来清空输入框，用户发完信息输入框就变空
    #history：刷新聊天界面，显示最新的对话
    return "",history

#绘制网页界面
#Blocks是Gradio的自定义布局模式，可以自由摆放组件，比现成的ChatInterface更灵活
with gr.Blocks(title="智能知识库问答系统") as demo:
    # gr.State 每个用户独立，刷新页面就会重新生成
    session_id = gr.State(lambda: uuid.uuid4().hex)

    gr.Markdown("知识库问答系统")
    gr.Markdown("基于RAG检索增强生成技术，上传TXT/PDF文档即可自然语言问答")
    gr.Markdown("使用说明：上传文档后即可提问，支持多轮对话追问")

    #Row：横向排列,把页面分成左右两列
    with gr.Row():

        #左列：文档上传区域，scale=1表示宽度占1份
        with gr.Column(scale=1):
            gr.Markdown("文档上传")

            #文件上传组件，只允许上传txt和pdf格式
            file_upload = gr.File(
                label="选择文件上传",
                file_types=[".txt", ".pdf"]
            )
            #上传状态显示框，interactive=False表示用户不能编辑，只用来显示结果
            upload_status = gr.Textbox(label="上传状态", interactive=False)
            #上传按钮，variant="primary"表示主按钮样式
            upload_btn = gr.Button("上传文档", variant="primary")

        #右列：聊天区域，scale=3表示宽度占3份，比左列宽
        with gr.Column(scale=3):
            #聊天框组件，设置高度为500像素
            chatbot = gr.Chatbot(height=500)

            #消息输入框，placeholder是灰色提示文字
            msg_input = gr.Textbox(
                label="输入问题",
                placeholder="输入问题后按回车或点击发送"
            )

            with gr.Row():
                submit_btn = gr.Button("发送", variant="primary")
                clear_btn = gr.Button("清空对话")


#绑定按钮事件
#哪个组件 + 发生什么事情 + 调用哪个函数 + 用什么当输入 + 结果输出到哪

# 上传按钮点击事件：点按钮就调用upload_document函数
# 输入：文件组件里的文件路径
# 输出：结果显示到上传状态文本框
    upload_btn.click(
        fn=upload_document,
        inputs=file_upload,
        outputs=upload_status
    )

#发送按钮点击事件：点发送就调用chat_respond
#输入：输入框内容 + 聊天历史
#输出：清空输入框 + 更新聊天历史界面
    submit_btn.click(
        fn=chat_respond,
        inputs=[msg_input, chatbot, session_id],
        outputs=[msg_input, chatbot]
    )

    msg_input.submit(
        fn=chat_respond,
        inputs=[msg_input, chatbot, session_id],
        outputs=[msg_input, chatbot]
    )

#清空按钮点击事件：点击后返回空列表，清空聊天历史
#lambda是匿名函数，不用单独写一个函数，直接返回空列表
    clear_btn.click(
        fn=lambda: [],
        inputs=None,
        outputs=chatbot
    )

#启动网页服务
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0")
