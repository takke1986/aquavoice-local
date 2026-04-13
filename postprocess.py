"""Claude API による文字起こし後処理（句読点追加・文法整形）。"""

import anthropic


def postprocess(text: str, terms: list[str], api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    terms_str = "、".join(terms) if terms else "なし"

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": (
                "以下の音声文字起こし結果に句読点を追加し、自然な日本語に整えてください。\n"
                f"専門用語リスト: {terms_str}\n"
                f"文字起こし: {text}\n\n"
                "整えた文章のみを返してください。説明は不要です。"
            ),
        }],
    )
    return msg.content[0].text.strip()
