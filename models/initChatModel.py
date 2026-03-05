# pip install langchain langchain-openai langchain-anthropic langchain-google-vertexai

from langchain.chat_models import init_chat_model

o3_mini = init_chat_model("openai:o3-mini", temperature=0)
claude_sonnet = init_chat_model("anthropic:claude-sonnet-4-5-20250929", temperature=0)
gemini_2_5_flash = init_chat_model("google_vertexai:gemini-2.5-flash", temperature=0)

o3_mini.invoke("what's your name")
claude_sonnet.invoke("what's your name")
gemini_2_5_flash.invoke("what's your name")


# pip install langchain langchain-openai langchain-anthropic

from langchain.chat_models import init_chat_model

# (We don't need to specify configurable=True if a model isn't specified.)
configurable_model = init_chat_model(temperature=0)

configurable_model.invoke("what's your name", config={"configurable": {"model": "gpt-4o"}})
# Use GPT-4o to generate the response

configurable_model.invoke(
    "what's your name",
    config={"configurable": {"model": "claude-sonnet-4-5-20250929"}},
)



# pip install langchain langchain-openai langchain-anthropic

from langchain.chat_models import init_chat_model

configurable_model_with_default = init_chat_model(
    "openai:gpt-4o",        # 默认模型：GPT-4o
    configurable_fields="any", # 所有参数都可在运行时修改
    config_prefix="foo",    # 配置键加上 "foo_" 前缀
    temperature=0,          # 默认 temperature
)

configurable_model_with_default.invoke("what's your name")
# GPT-4o response with temperature 0 (as set in default)

configurable_model_with_default.invoke(
    "what's your name",
    config={
        "configurable": {
            "foo_model": "anthropic:claude-sonnet-4-5-20250929",
            "foo_temperature": 0.6,
        }
    },
)
# Override default to use Sonnet 4.5 with temperature 0.6 to generate response
# 两个不同职责的模型
chat_model   = init_chat_model("openai:gpt-4o", config_prefix="chat")
summary_model = init_chat_model("openai:gpt-4o", config_prefix="summary")

# 同时配置两个，互不干扰
config = {
    "configurable": {
        "chat_model": "openai:gpt-4o",
        "chat_temperature": 0.8,
        "summary_model": "anthropic:claude-sonnet-4-5-20250929",
        "summary_temperature": 0.2,
    }
}

# pip install langchain langchain-openai langchain-anthropic

from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

class GetWeather(BaseModel):
    '''Get the current weather in a given location'''

    location: str = Field(..., description="The city and state, e.g. San Francisco, CA")

class GetPopulation(BaseModel):
    '''Get the current population in a given location'''

    location: str = Field(..., description="The city and state, e.g. San Francisco, CA")

configurable_model = init_chat_model(
    "gpt-4o", configurable_fields=("model", "model_provider"), temperature=0
)

configurable_model_with_tools = configurable_model.bind_tools(
    [
        GetWeather,
        GetPopulation,
    ]
)
configurable_model_with_tools.invoke(
    "Which city is hotter today and which is bigger: LA or NY?"
)
# Use GPT-4o

configurable_model_with_tools.invoke(
    "Which city is hotter today and which is bigger: LA or NY?",
    config={"configurable": {"model": "claude-sonnet-4-5-20250929"}},
)
# Use Sonnet 4.5