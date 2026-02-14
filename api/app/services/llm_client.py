"""LLM 客戶端抽象介面與 OpenAI 實作。"""

from typing import Protocol, runtime_checkable

from openai import AsyncOpenAI


@runtime_checkable
class LLMClient(Protocol):
    """LLM 客戶端介面，定義統一的文字生成方法。"""

    async def generate(self, system_prompt: str, user_message: str) -> str: ...


class OpenAIClient:
    """使用 OpenAI API 的 LLM 客戶端實作。"""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini", temperature: float = 0.3):
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._temperature = temperature

    async def generate(self, system_prompt: str, user_message: str) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            temperature=self._temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content or ""
