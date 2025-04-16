import gradio as gr
import time
import os
from llm import LLM, model_name
import PyPDF2
import pandas as pd
from docx import Document

# 创建LLM实例
llm = LLM(model_name=model_name)

# 定义处理用户消息的函数
def respond(message, chat_history):
    """处理用户消息并返回AI响应"""
    if not message.strip():
        return "", chat_history
        
    # 获取LLM响应
    bot_message = llm.get_response(message)
    
    # 更新聊天历史
    chat_history.append((message, bot_message))
    
    return "", chat_history

# 定义清除历史的函数
def clear_history():
    """清除对话历史"""
    llm.clear_history()
    return None

# 定义文件处理函数
def process_file(file):
    """处理上传的文件并将内容添加到对话历史"""
    if file is None:
        return None, "请先上传文件"
    
    file_path = file.name
    file_name = os.path.basename(file_path)
    file_ext = os.path.splitext(file_name)[1].lower()
    
    try:
        if file_ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        
        elif file_ext == ".pdf":
            content = ""
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num in range(len(pdf_reader.pages)):
                    content += pdf_reader.pages[page_num].extract_text() + "\n\n"
        
        elif file_ext == ".docx":
            doc = Document(file_path)
            content = "\n".join([para.text for para in doc.paragraphs])
            
        elif file_ext in [".csv", ".xlsx", ".xls"]:
            if file_ext == ".csv":
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            content = df.to_string()
            
        else:
            return None, f"不支持的文件格式: {file_ext}"
        
        # 检查内容长度，过长则截断
        if len(content) > 50000:  # 设置合理的长度限制
            content = content[:50000] + "\n\n[文件内容过长，已截断...]"
            
        # 将文件内容添加到对话历史中
        response = llm.add_file_content(content, file_name)
        
        return [(f"已上传文件: {file_name}", response)], f"文件'{file_name}'已成功处理"
        
    except Exception as e:
        return None, f"处理文件时出错: {str(e)}"

# 创建Gradio界面
with gr.Blocks(css="footer {visibility: hidden}") as demo:
    gr.Markdown("# 交互式LLM对话系统")
    
    # 文件上传组件
    with gr.Row():
        file_input = gr.File(label="上传文件", file_types=["txt", "pdf", "docx", "csv", "xlsx", "xls"])
        file_status = gr.Textbox(label="文件状态", interactive=False)
    
    # 上传按钮
    upload_btn = gr.Button("处理文件")
    
    # 聊天组件
    chatbot = gr.Chatbot(
        height=500,
        bubble_full_width=False,
        avatar_images=(None, "https://api.dicebear.com/7.x/bottts/svg?seed=assistant"),
        show_copy_button=True,
    )
    
    # 用户输入框和发送按钮
    with gr.Row():
        msg = gr.Textbox(
            placeholder="在这里输入您的问题...", 
            container=False, 
            scale=9,
            show_label=False,
        )
        submit_btn = gr.Button("发送", scale=1)
    
    # 清除按钮
    clear_btn = gr.Button("清除对话历史")
    
    # 设置事件处理
    submit_btn.click(
        respond, 
        [msg, chatbot], 
        [msg, chatbot],
    )
    msg.submit(
        respond, 
        [msg, chatbot], 
        [msg, chatbot],
    )
    clear_btn.click(
        clear_history, 
        None, 
        chatbot,
    )
    upload_btn.click(
        process_file,
        [file_input],
        [chatbot, file_status],
    )
    
    # 使用说明
    gr.Markdown("""
    ## 使用说明
    - 上传文件：支持TXT、PDF、DOCX、CSV、XLSX等格式
    - 上传后点击"处理文件"按钮，文件内容会被添加到对话历史中
    - 在输入框中输入您的问题，然后按回车或点击"发送"按钮
    - 点击"清除对话历史"按钮可以开始新的对话
    - 系统会记住对话历史，保持上下文连贯
    """)

# 启动Gradio应用
if __name__ == "__main__":
    demo.launch(share=False)  # 设置share=True可以生成公共链接