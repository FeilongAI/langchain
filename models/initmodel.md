# init_chat_model

> **函数**，位于 `langchain` 库中

📖 [在文档中查看](https://reference.langchain.com/python/langchain/chat_models/base/init_chat_model)

使用统一接口，从任意受支持的提供商初始化一个聊天模型。

**两种主要使用场景：**

1. **固定模型** —— 提前指定模型，获得一个可直接使用的聊天模型。
2. **可配置模型** —— 在运行时通过 `config` 动态指定参数（包括模型名称），无需修改代码即可在不同模型/提供商之间切换。

> **注意：安装要求**
>
> 需要安装所选模型提供商对应的集成包。
> 具体包名请参阅下方的 `model_provider` 参数说明（例如 `pip install langchain-openai`）。
> 支持的模型参数请参阅[提供商集成的 API 参考文档](https://docs.langchain.com/oss/python/integrations/providers)。

---

## 函数签名

```python
init_chat_model(
    model: str | None = None,
    *,
    model_provider: str | None = None,
    configurable_fields: Literal['any'] | list[str] | tuple[str, ...] | None = None,
    config_prefix: str | None = None,
    **kwargs: Any = {},
) -> BaseChatModel | _ConfigurableModel
```

---

## 使用示例

### 初始化一个固定（不可配置）模型

```python
# pip install langchain langchain-openai langchain-anthropic langchain-google-vertexai

from langchain.chat_models import init_chat_model

o3_mini = init_chat_model("openai:o3-mini", temperature=0)
claude_sonnet = init_chat_model("anthropic:claude-sonnet-4-5-20250929", temperature=0)
gemini_flash = init_chat_model("google_vertexai:gemini-2.5-flash", temperature=0)

o3_mini.invoke("你叫什么名字？")
claude_sonnet.invoke("你叫什么名字？")
gemini_flash.invoke("你叫什么名字？")
```

### 无默认值的部分可配置模型

```python
# pip install langchain langchain-openai langchain-anthropic

from langchain.chat_models import init_chat_model

# 未指定模型时，无需设置 configurable=True
configurable_model = init_chat_model(temperature=0)

configurable_model.invoke(
    "你叫什么名字？",
    config={"configurable": {"model": "gpt-4o"}}
)
# 使用 GPT-4o 生成回复

configurable_model.invoke(
    "你叫什么名字？",
    config={"configurable": {"model": "claude-sonnet-4-5-20250929"}},
)
# 使用 Sonnet 4.5 生成回复
```

### 有默认值的完全可配置模型

```python
# pip install langchain langchain-openai langchain-anthropic

from langchain.chat_models import init_chat_model

configurable_model_with_default = init_chat_model(
    "openai:gpt-4o",
    configurable_fields="any",  # 允许在运行时配置 temperature、max_tokens 等参数
    config_prefix="foo",
    temperature=0,
)

configurable_model_with_default.invoke("你叫什么名字？")
# 使用默认设置（temperature=0）的 GPT-4o 生成回复

configurable_model_with_default.invoke(
    "你叫什么名字？",
    config={
        "configurable": {
            "foo_model": "anthropic:claude-sonnet-4-5-20250929",
            "foo_temperature": 0.6,
        }
    },
)
# 覆盖默认值，改用 temperature=0.6 的 Sonnet 4.5 生成回复
```

### 为可配置模型绑定工具

可以像操作普通模型一样，对可配置模型调用任何声明式方法：

```python
# pip install langchain langchain-openai langchain-anthropic

from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

class GetWeather(BaseModel):
    '''获取指定地点的当前天气'''
    location: str = Field(..., description="城市和州，例如 San Francisco, CA")

class GetPopulation(BaseModel):
    '''获取指定地点的当前人口'''
    location: str = Field(..., description="城市和州，例如 San Francisco, CA")

configurable_model = init_chat_model(
    "gpt-4o", configurable_fields=("model", "model_provider"), temperature=0
)

configurable_model_with_tools = configurable_model.bind_tools(
    [GetWeather, GetPopulation]
)

configurable_model_with_tools.invoke("今天洛杉矶和纽约哪个更热？哪个城市更大？")
# 使用 GPT-4o

configurable_model_with_tools.invoke(
    "今天洛杉矶和纽约哪个更热？哪个城市更大？",
    config={"configurable": {"model": "claude-sonnet-4-5-20250929"}},
)
# 使用 Sonnet 4.5
```

---

## 参数说明

| 参数名 | 类型 | 是否必填 | 描述 |
|--------|------|----------|------|
| `model` | `str \| None` | 否 | 模型名称，可选择加上提供商前缀（如 `'openai:gpt-4o'`）。建议使用提供商文档中的精确模型 ID（如带日期的版本 `'...-20250514'`）而非别名，以确保行为可靠。若未指定 `model_provider`，将尝试从模型名称推断。以下前缀对应的提供商将被自动推断：`gpt-...`/`o1...`/`o3...` → `openai`；`claude...` → `anthropic`；`amazon...` → `bedrock`；`gemini...` → `google_vertexai`；`command...` → `cohere`；`accounts/fireworks...` → `fireworks`；`mistral...` → `mistralai`；`deepseek...` → `deepseek`；`grok...` → `xai`；`sonar...` → `perplexity`；`solar...` → `upstage`。（默认值：`None`） |
| `model_provider` | `str \| None` | 否 | 模型提供商，若未在 `model` 参数中指定则需在此提供（见上方说明）。支持的提供商及对应集成包：`openai` → `langchain-openai`；`anthropic` → `langchain-anthropic`；`azure_openai` → `langchain-openai`；`google_vertexai` → `langchain-google-vertexai`；`google_genai` → `langchain-google-genai`；`bedrock` → `langchain-aws`；`cohere` → `langchain-cohere`；`fireworks` → `langchain-fireworks`；`mistralai` → `langchain-mistralai`；`groq` → `langchain-groq`；`ollama` → `langchain-ollama`；`deepseek` → `langchain-deepseek`；`xai` → `langchain-xai` 等。（默认值：`None`） |
| `configurable_fields` | `Literal['any'] \| list[str] \| tuple[str, ...] \| None` | 否 | 指定哪些模型参数在运行时可配置：`None` 表示无可配置字段（固定模型）；`'any'` 表示所有字段均可配置（**注意安全风险，见下方说明**）；`list[str] \| tuple[str, ...]` 表示仅指定字段可配置。若已指定 `model`，默认为 `None`；若未指定 `model`，默认为 `("model", "model_provider")`。⚠️ **安全提示**：设置 `configurable_fields="any"` 意味着 `api_key`、`base_url` 等字段可在运行时被修改，可能导致模型请求被重定向到其他服务/用户。若接受不受信任的配置，请通过 `configurable_fields=(...)` 明确枚举允许配置的字段。（默认值：`None`） |
| `config_prefix` | `str \| None` | 否 | 配置键的可选前缀。当同一应用中存在多个可配置模型时非常有用。若 `config_prefix` 为非空字符串，则模型可通过 `config["configurable"]["{config_prefix}_{param}"]` 在运行时配置。（默认值：`None`） |
| `**kwargs` | `Any` | 否 | 传递给底层聊天模型 `__init__` 方法的额外关键字参数。常用参数包括：`temperature`（控制随机性的模型温度）、`max_tokens`（最大输出 token 数）、`timeout`（等待响应的最长时间，单位秒）、`max_retries`（失败请求的最大重试次数）、`base_url`（自定义 API 端点 URL）、`rate_limiter`（用于控制请求频率的限速器实例）。（默认值：`{}`） |

---

## 返回值

`BaseChatModel | _ConfigurableModel`

- 若推断为**不可配置**，返回与指定 `model_name` 和 `model_provider` 对应的 `BaseChatModel` 实例。
- 若推断为**可配置**，返回一个聊天模型模拟器，待传入 `config` 后在运行时初始化底层模型。

---

[在 GitHub 上查看源码](https://github.com/langchain-ai/langchain/blob/f698b43b9af456949f96998f6a99c9289880a815/libs/langchain_v1/langchain/chat_models/base.py#L208)