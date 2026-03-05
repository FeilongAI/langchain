import  os
from langchain.chat_models import  init_chat_model


model = init_chat_model(
    model="Qwen/Qwen3-VL-30B-A3B-Instruct",
    model_provider="openai",   # 模型提供商，设为 "openai" 表示使用 OpenAI 兼容协议
    base_url="",
    api_key="",
)
response = model.invoke("你好")

print(response)