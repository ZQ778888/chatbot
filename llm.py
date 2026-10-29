from openai import OpenAI

from config import get_settings


def build_client() -> OpenAI:
    settings = get_settings()
    if not settings.api_key.get_secret_value():
        raise SystemExit("缺少 CHATBOT_API_KEY，请在 .env 中配置后重新运行。")
    return OpenAI(
        api_key=settings.api_key.get_secret_value(),
        base_url=settings.base_url,
    )


def chat_once(client: OpenAI, messages: list[dict]) -> str:
    settings = get_settings()
    response = client.chat.completions.create(
        model=settings.model,
        messages=messages,
        temperature=settings.temperature,
        stream=False,
    )
    return response.choices[0].message.content or ""
def chat_stream(client: OpenAI, messages: list[dict]):
    settings = get_settings()
    stream = client.chat.completions.create(
        model=settings.model,
        messages=messages,
        temperature=settings.temperature,
        stream=True,  # 开启流式
    )
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content is not None:
            yield content