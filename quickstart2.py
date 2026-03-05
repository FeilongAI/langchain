# =============================================================================
# LangChain Agent 快速入门示例
# 这个示例展示了如何创建一个具有工具调用能力、上下文管理和结构化输出的 AI Agent
# =============================================================================

from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool, ToolRuntime
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.structured_output import ToolStrategy


# =============================================================================
# 系统提示词 (System Prompt)
# 定义 Agent 的角色和行为方式
# 这里设定 Agent 是一个喜欢用双关语的天气预报专家
# =============================================================================
SYSTEM_PROMPT = """You are an expert weather forecaster, who speaks in puns.

You have access to two tools:

- get_weather_for_location: use this to get the weather for a specific location
- get_user_location: use this to get the user's location

If a user asks you for the weather, make sure you know the location. If you can tell from the question that they mean wherever they are, use the get_user_location tool to find their location."""


# =============================================================================
# 上下文 Schema (Context Schema)
# 用于在工具执行时传递额外的运行时信息
# 这里定义了一个简单的上下文，只包含用户ID
# =============================================================================
@dataclass
class Context:
    """
    自定义运行时上下文 schema。

    上下文的作用：
    - 在 Agent 运行期间传递不属于对话消息的额外信息
    - 工具可以通过 ToolRuntime 访问这些上下文数据
    - 常见用途：用户身份验证信息、会话数据、配置参数等
    """
    user_id: str  # 用户唯一标识符，工具可以根据此ID获取用户相关信息


# =============================================================================
# 工具定义 (Tools)
# 工具是 Agent 可以调用的函数，用于执行特定任务
# 使用 @tool 装饰器将普通函数转换为 Agent 可调用的工具
# =============================================================================

@tool
def get_weather_for_location(city: str) -> str:
    """
    获取指定城市的天气信息。

    参数:
        city (str): 城市名称

    返回:
        str: 天气描述字符串

    注意: 这是一个模拟函数，实际应用中应该调用真实的天气API
    """
    return f"It's always sunny in {city}!"


@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """
    根据用户ID获取用户所在位置。

    参数:
        runtime (ToolRuntime[Context]): 工具运行时对象，包含上下文信息
            - ToolRuntime 是一个特殊类型，允许工具访问运行时上下文
            - 泛型参数 [Context] 指定了上下文的类型

    返回:
        str: 用户所在城市名称

    工作原理:
        通过 runtime.context 访问我们在调用 agent.invoke() 时传入的 Context 对象
    """
    user_id = runtime.context.user_id  # 从上下文中获取用户ID
    return "Florida" if user_id == "1" else "SF"  # 根据用户ID返回不同位置


# =============================================================================
# 模型配置 (Model Configuration)
# 配置用于 Agent 的大语言模型 (LLM)
# =============================================================================
model = ChatOpenAI(
    model="Qwen/Qwen3-VL-30B-A3B-Instruct",  # 模型名称/标识符
    api_key="",  # API 密钥
    base_url="",  # API 基础URL（用于兼容 OpenAI 格式的第三方服务）
)


# =============================================================================
# 响应格式 (Response Format)
# 定义 Agent 返回的结构化响应格式
# 使用 dataclass 确保输出遵循预定义的结构
# =============================================================================
@dataclass
class ResponseFormat:
    """
    Agent 的结构化响应 schema。

    作用:
        - 强制 Agent 按照指定格式返回数据
        - 便于程序解析和处理 Agent 的输出
        - 可以定义必填字段和可选字段
    """
    # 双关语回复（必填字段）
    # Agent 必须在每次响应中提供这个字段
    punny_response: str

    # 天气状况信息（可选字段）
    # 使用 str | None 表示这个字段可以为 None
    # 只有当 Agent 实际获取了天气信息时才会填充此字段
    weather_conditions: str | None = None


# =============================================================================
# 内存/检查点设置 (Memory/Checkpointer Setup)
# 用于保存对话历史，实现多轮对话能力
# =============================================================================
checkpointer = InMemorySaver()
"""
InMemorySaver 的作用:
    - 在内存中保存对话状态（消息历史、中间结果等）
    - 允许 Agent 记住之前的对话内容，实现上下文连续性
    - 通过 thread_id 区分不同的对话会话

注意:
    - InMemorySaver 数据存储在内存中，程序重启后会丢失
    - 生产环境中可以使用 SQLiteSaver、PostgresSaver 等持久化存储
"""


# =============================================================================
# 创建 Agent
# 将所有组件组合在一起创建完整的 Agent
# =============================================================================
agent = create_agent(
    model=model,                                    # 使用的语言模型
    system_prompt=SYSTEM_PROMPT,                    # 系统提示词，定义 Agent 行为
    tools=[get_user_location, get_weather_for_location],  # Agent 可用的工具列表
    context_schema=Context,                         # 上下文 schema，定义可传递的上下文类型
    response_format=ToolStrategy(ResponseFormat),   # 响应格式策略
    checkpointer=checkpointer                       # 检查点/内存管理器
)
"""
ToolStrategy(ResponseFormat) 说明:
    - ToolStrategy 是一种将结构化输出作为工具调用的策略
    - Agent 会将最终响应格式化为 ResponseFormat 定义的结构
    - 这确保了输出的一致性和可解析性
"""


# =============================================================================
# 运行 Agent - 第一次对话
# =============================================================================

# 配置对象，包含会话标识
# thread_id 用于标识一个独立的对话会话
# 相同的 thread_id 会共享对话历史
config = {"configurable": {"thread_id": "1"}}

# 调用 Agent 处理用户消息
response = agent.invoke(
    # messages: 对话消息列表，这里只包含一条用户消息
    {"messages": [{"role": "user", "content": "what is the weather outside?"}]},
    config=config,      # 会话配置（包含 thread_id）
    context=Context(user_id="1")  # 运行时上下文，传递用户ID
)

# 打印结构化响应
# structured_response 包含按 ResponseFormat 格式化的输出
print(response['structured_response'])
# 输出示例:
# ResponseFormat(
#     punny_response="Florida is still having a 'sun-derful' day! ...",
#     weather_conditions="It's always sunny in Florida!"
# )


# =============================================================================
# 运行 Agent - 继续对话（多轮对话演示）
# 使用相同的 thread_id 继续之前的对话
# =============================================================================
response = agent.invoke(
    {"messages": [{"role": "user", "content": "thank you!"}]},
    config=config,  # 使用相同的 config（相同的 thread_id）
    context=Context(user_id="1")
)

print(response['structured_response'])
# 输出示例:
# ResponseFormat(
#     punny_response="You're 'thund-erfully' welcome! ...",
#     weather_conditions=None  # 这次没有查询天气，所以为 None
# )