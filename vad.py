"""Silero-VAD による音声区間検出と幻覚フィルター。"""

import collections
import unicodedata
from typing import Optional

import numpy as np
import torch
from silero_vad import VADIterator, load_silero_vad

SAMPLE_RATE = 16000
CHUNK_SAMPLES = 512
PRE_BUFFER_CHUNKS = 10   # 発話前の約320msを保持
MIN_SPEECH_SEC = 0.5     # これより短い発話は無視

HALLUCINATIONS: frozenset[str] = frozenset({
    "thank you", "thanks", "thank you very much",
    "thank you for watching", "you", "bye", "bye bye",
    "ありがとうございました", "ありがとうございます",
    "ご視聴ありがとうございました", "字幕",
})

import re

# 日本語（ひらがな・カタカナ・漢字）・英数字・基本記号・空白のみ許可
_FOREIGN_RE = re.compile(
    r"[^\u3040-\u30FF"   # ひらがな・カタカナ
    r"\u3400-\u9FFF"     # 漢字（CJK統合漢字）
    r"\uF900-\uFAFF"     # CJK互換漢字
    r"\uFF00-\uFFEF"     # 全角英数・記号
    r"\u3000-\u303F"     # 日本語句読点
    r"a-zA-Z0-9"         # 英数字
    r"\s"                # 空白
    r"!-~"               # 基本ASCII記号（! " # ... ~）
    r"]",
    re.UNICODE,
)


def remove_foreign_scripts(text: str) -> str:
    """アラビア語・ヘブライ語など日本語・英語以外の文字を除去する。"""
    cleaned = _FOREIGN_RE.sub("", text).strip()
    if cleaned != text.strip():
        print(f"[VAD] 外国語文字を除去: {repr(text)} → {repr(cleaned)}")
    return cleaned


def is_hallucination(text: str) -> bool:
    return text.strip().lower() in HALLUCINATIONS


class VADProcessor:
    def __init__(self, threshold: float = 0.5, min_silence_ms: int = 800) -> None:
        model = load_silero_vad()
        self._vad = VADIterator(
            model,
            threshold=threshold,
            sampling_rate=SAMPLE_RATE,
            min_silence_duration_ms=min_silence_ms,
            speech_pad_ms=100,
        )
        self._pre: collections.deque[np.ndarray] = collections.deque(maxlen=PRE_BUFFER_CHUNKS)
        self._buf: list[float] = []
        self._speaking = False

    @property
    def speaking(self) -> bool:
        return self._speaking

    def process(self, chunk: np.ndarray) -> tuple[Optional[bool], Optional[np.ndarray]]:
        """
        Returns:
            speaking_changed: True=発話開始, False=発話終了, None=変化なし
            audio: 発話終了時に音声データ、それ以外は None
        """
        tensor = torch.from_numpy(chunk.astype(np.float32))
        result = self._vad(tensor)

        speaking_changed: Optional[bool] = None
        audio: Optional[np.ndarray] = None

        if result:
            if "start" in result and not self._speaking:
                self._speaking = True
                speaking_changed = True
                for pre in self._pre:
                    self._buf.extend(pre.tolist())
                self._buf.extend(chunk.tolist())
            elif "end" in result and self._speaking:
                self._buf.extend(chunk.tolist())
                self._speaking = False
                speaking_changed = False
                if len(self._buf) >= SAMPLE_RATE * MIN_SPEECH_SEC:
                    audio = np.array(self._buf, dtype=np.float32)
                self._buf = []
        elif self._speaking:
            self._buf.extend(chunk.tolist())
        else:
            self._pre.append(chunk.copy())

        return speaking_changed, audio

    def reset(self) -> None:
        self._vad.reset_states()
        self._pre.clear()
        self._buf = []
        self._speaking = False
