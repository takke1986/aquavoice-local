"""sounddevice でマイクを直接キャプチャする。"""

import queue
import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000
CHUNK_SIZE = 512  # silero-vad が要求するサイズ


class AudioCapture:
    def __init__(self) -> None:
        self._queue: queue.Queue[np.ndarray] = queue.Queue()
        self._stream: sd.InputStream | None = None

    def start(self) -> None:
        self._queue = queue.Queue()  # 古いデータをフラッシュ
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype=np.float32,
            blocksize=CHUNK_SIZE,
            callback=self._callback,
        )
        self._stream.start()

    def stop(self) -> None:
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def _callback(self, indata: np.ndarray, frames: int, time, status) -> None:
        self._queue.put(indata[:, 0].copy())

    def get_chunk(self, timeout: float = 0.1) -> np.ndarray | None:
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None
