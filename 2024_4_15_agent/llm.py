from openai import OpenAI
import time
import sys
import os

class LLM():
    base_url = "https://openrouter.ai/api/v1"
    api_key = "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"
    
    def __init__(self, model_name="anthropic/claude-3.5-sonnet"):
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        self.model_name = model_name
        self.conversation_history = []
        
    def add_message(self, role, content):
        """添加消息到对话历史"""
        self.conversation_history.append({"role": role, "content": content})
        
    def get_response(self, user_input):
        """获取LLM响应"""
        # 添加用户消息到历史
        self.add_message("user", user_input)
        
        try:
            # 调用API获取响应
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.conversation_history,
                temperature=0.7,
            )
            
            # 提取助手回复
            assistant_message = response.choices[0].message.content
            
            # 将助手回复添加到历史
            self.add_message("assistant", assistant_message)
            
            return assistant_message
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    def clear_history(self):
        """清除对话历史"""
        self.conversation_history = []
        
    def add_file_content(self, content, filename):
        """添加文件内容到对话历史"""
        file_message = f"我上传了一个名为'{filename}'的文件，内容如下:\n\n{content}"
        self.add_message("user", file_message)
        return f"我已经读取了文件'{filename}'的内容，现在您可以基于这个文件内容提问。"


# 全局变量
model_name = "anthropic/claude-3.5-sonnet"
OPENROUTER_API_KEY = "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"
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"


def create_agent():
    """创建并返回一个LLM实例"""
    return LLM(model_name=model_name)


def interactive_chat():
    """交互式对话系统主函数"""
    print("\n欢迎使用交互式LLM对话系统!")
    print("------------------------------")
    print("输入您的问题与AI进行对话")
    print("输入 'exit' 或 'quit' 退出对话")
    print("输入 'clear' 清除对话历史")
    print("------------------------------\n")
    
    # 创建LLM实例
    agent = create_agent()
    
    # 对话循环
    while True:
        # 获取用户输入
        user_input = input("\n用户: ")
        
        # 检查退出命令
        if user_input.lower() in ['exit', 'quit']:
            print("\n再见！")
            break
        
        # 检查清除历史命令
        elif user_input.lower() == 'clear':
            agent.clear_history()
            print("\n对话历史已清除")
            continue
        
        # 空输入处理
        elif not user_input.strip():
            print("请输入有效内容")
            continue
        
        # 处理正常输入
        print("\nAI思考中...", end="", flush=True)
        
        # 获取AI响应
        response = agent.get_response(user_input)
        
        # 清除思考提示
        sys.stdout.write("\r" + " " * 20 + "\r")
        sys.stdout.flush()
        
        # 显示回复
        print(f"\nAI: {response}")


if __name__ == "__main__":
    interactive_chat()