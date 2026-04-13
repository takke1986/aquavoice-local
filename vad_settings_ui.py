"""マイク感度設定ウィンドウ（別プロセスで起動）。"""

import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import load_settings, save_settings


def main() -> None:
    settings = load_settings()

    root = tk.Tk()
    root.title("マイク感度の調整 — KoeType")
    root.geometry("400x260")
    root.resizable(False, False)

    # ---- 説明 ----
    desc_frame = ttk.LabelFrame(root, text="VAD閾値（Voice Activity Detection）", padding=12)
    desc_frame.pack(fill=tk.X, padx=12, pady=(12, 4))

    ttk.Label(desc_frame, text="値が高いほど、はっきりした声しか拾いません。", foreground="gray").pack(anchor=tk.W)

    # ---- スライダー ----
    slider_frame = ttk.Frame(desc_frame)
    slider_frame.pack(fill=tk.X, pady=(8, 0))

    ttk.Label(slider_frame, text="敏感\n0.3").pack(side=tk.LEFT)

    threshold_var = tk.DoubleVar(value=settings.vad_threshold)

    slider = ttk.Scale(
        slider_frame,
        from_=0.3,
        to=0.9,
        orient=tk.HORIZONTAL,
        variable=threshold_var,
        command=lambda _: _update_label(),
    )
    slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)

    ttk.Label(slider_frame, text="鈍感\n0.9").pack(side=tk.RIGHT)

    # ---- 現在値の表示 ----
    value_label = ttk.Label(desc_frame, text="", font=("", 14, "bold"))
    value_label.pack(pady=(6, 0))

    def _update_label() -> None:
        v = round(threshold_var.get(), 2)
        if v <= 0.4:
            hint = "（敏感：小声・ノイズも拾う）"
        elif v <= 0.6:
            hint = "（標準）"
        elif v <= 0.75:
            hint = "（やや鈍感）"
        else:
            hint = "（鈍感：はっきりした声のみ）"
        value_label.config(text=f"{v:.2f}　{hint}")

    _update_label()

    # ---- プリセットボタン ----
    preset_frame = ttk.Frame(root, padding=(12, 0))
    preset_frame.pack(fill=tk.X)
    ttk.Label(preset_frame, text="プリセット:").pack(side=tk.LEFT)
    for label, val in [("敏感 (0.3)", 0.3), ("標準 (0.5)", 0.5), ("鈍感 (0.7)", 0.7)]:
        ttk.Button(
            preset_frame, text=label,
            command=lambda v=val: [threshold_var.set(v), _update_label()]
        ).pack(side=tk.LEFT, padx=(6, 0))

    # ---- 保存ボタン ----
    def save() -> None:
        settings.vad_threshold = round(threshold_var.get(), 2)
        save_settings(settings)
        root.destroy()

    btn_frame = ttk.Frame(root, padding=(12, 8, 12, 12))
    btn_frame.pack(fill=tk.X)
    ttk.Button(btn_frame, text="保存", command=save).pack(side=tk.RIGHT)
    ttk.Button(btn_frame, text="キャンセル", command=root.destroy).pack(side=tk.RIGHT, padx=(0, 8))

    ttk.Label(
        btn_frame, text="※ 次回の録音開始から反映されます",
        foreground="gray", font=("", 10)
    ).pack(side=tk.LEFT)

    root.mainloop()


if __name__ == "__main__":
    main()
