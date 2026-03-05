import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()
BASE_URL = os.getenv("BASE_URL")  # 假设 .env 文件中有 BASE_URL=your_base_url
API_KEY = os.getenv("API_KEY")
model = init_chat_model(
    model="Qwen/Qwen3-VL-30B-A3B-Instruct",
    model_provider="openai",
    base_url=BASE_URL,
    api_key=API_KEY,
)
## 调用模型最直接的方法
response = model.invoke("Why do parrots have colorful feathers?")
print(response)
#可以向聊天模型提供消息列表以表示对话历史。每个消息都有一个角色，模型使用该角色来指示谁在对话中发送了消息。
conversation = [
    {"role": "system", "content": "You are a helpful assistant that translates English to French."},
    {"role": "user", "content": "Translate: I love programming."},
    {"role": "assistant", "content": "J'adore la programmation."},
    {"role": "user", "content": "Translate: I love building applications."}
]

response = model.invoke(conversation)
print(response)  # AIMessage("J'adore créer des applications.")


from langchain.messages import HumanMessage, AIMessage, SystemMessage
#消息对象调用
conversation = [
    SystemMessage("You are a helpful assistant that translates English to French."),
    HumanMessage("Translate: I love programming."),
    AIMessage("J'adore la programmation."),
    HumanMessage("Translate: I love building applications.")
]

response = model.invoke(conversation)
print(response)  # AIMessage("J'adore créer des applications.")