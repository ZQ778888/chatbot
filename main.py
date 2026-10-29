from config import get_settings
from llm import build_client, chat_stream


def main() -> None:
    settings = get_settings()
    try:
        client = build_client()
    except SystemExit as exc:
        print(exc)
        return

    messages = [{"role": "system", "content": settings.system_prompt}]
    print("聊天机器人已启动，输入 exit / quit 退出。")

    while True:
        user_input = input("\n你：").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})
        print("\n助手：", end="", flush=True)
        full_reply = ""
        for piece in chat_stream(client, messages):
            print(piece, end="", flush=True)
            full_reply += piece
        print()  # 结束后换行
        messages.append({"role": "assistant", "content": full_reply})


if __name__ == "__main__":
    main()