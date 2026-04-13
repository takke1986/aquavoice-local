"""Cohere Transcribe モデルの推論。日本語を直接指定して外国語誤認識を防ぐ。"""

import numpy as np
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

MODEL_ID = "CohereLabs/cohere-transcribe-03-2026"
LANGUAGE = "ja"
MAX_NEW_TOKENS = 256


def _device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


class Transcriber:
    def __init__(self) -> None:
        self._device = _device()
        print(f"[Transcriber] device={self._device}")
        self._processor = AutoProcessor.from_pretrained(MODEL_ID)
        self._model = AutoModelForSpeechSeq2Seq.from_pretrained(
            MODEL_ID, dtype=torch.float16
        ).to(self._device)
        print(f"[Transcriber] language={LANGUAGE}, ready.")

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> str:
        inputs = self._processor(
            audio.astype(np.float32),
            language=LANGUAGE,
            sampling_rate=sample_rate,
            return_tensors="pt",
        )
        model_inputs = {}
        for k, v in inputs.items():
            if not isinstance(v, torch.Tensor):
                continue
            dtype = torch.float16 if v.is_floating_point() else v.dtype
            model_inputs[k] = v.to(device=self._device, dtype=dtype)

        with torch.no_grad():
            out = self._model.generate(**model_inputs, max_new_tokens=MAX_NEW_TOKENS)

        return self._processor.batch_decode(out, skip_special_tokens=True)[0].strip()
