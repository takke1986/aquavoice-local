"""専門用語登録ウィンドウ（別プロセスで起動）。"""

import sys
import tkinter as tk
from tkinter import messagebox, ttk

# 別プロセスとして起動されるため、パスを追加
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import load_terms, save_terms


def main() -> None:
    root = tk.Tk()
    root.title("専門用語登録 — KoeType")
    root.geometry("560x460")
    root.resizable(True, True)

    terms = load_terms()

    # ---- リスト ----
    list_frame = ttk.Frame(root, padding=(10, 10, 10, 0))
    list_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(list_frame, text="登録済みの用語", font=("", 12, "bold")).pack(anchor=tk.W)

    lb_frame = ttk.Frame(list_frame)
    lb_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

    sb = ttk.Scrollbar(lb_frame)
    sb.pack(side=tk.RIGHT, fill=tk.Y)

    lb = tk.Listbox(lb_frame, yscrollcommand=sb.set, font=("", 13), selectmode=tk.SINGLE)
    lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb.config(command=lb.yview)

    def refresh() -> None:
        lb.delete(0, tk.END)
        for w, c in terms.items():
            lb.insert(tk.END, f"  {w}  →  {c}")

    refresh()

    # ---- 追加フォーム ----
    form = ttk.LabelFrame(root, text="用語を追加", padding=10)
    form.pack(fill=tk.X, padx=10, pady=8)

    form.columnconfigure(1, weight=1)
    form.columnconfigure(3, weight=1)

    ttk.Label(form, text="誤認識される表記:").grid(row=0, column=0, sticky=tk.W)
    wrong_var = tk.StringVar()
    ttk.Entry(form, textvariable=wrong_var).grid(row=0, column=1, sticky=tk.EW, padx=(4, 8))

    ttk.Label(form, text="→ 正しい表記:").grid(row=0, column=2, sticky=tk.W)
    correct_var = tk.StringVar()
    ttk.Entry(form, textvariable=correct_var).grid(row=0, column=3, sticky=tk.EW, padx=(4, 8))

    def add() -> None:
        w, c = wrong_var.get().strip(), correct_var.get().strip()
        if not w or not c:
            messagebox.showwarning("入力エラー", "両方の欄を入力してください", parent=root)
            return
        terms[w] = c
        save_terms(terms)
        refresh()
        wrong_var.set("")
        correct_var.set("")

    ttk.Button(form, text="追加", command=add).grid(row=0, column=4, padx=(4, 0))

    # ---- 削除ボタン ----
    def delete() -> None:
        sel = lb.curselection()
        if not sel:
            return
        item = lb.get(sel[0]).strip()
        w = item.split("  →  ")[0].strip()
        if w in terms:
            del terms[w]
            save_terms(terms)
            refresh()

    btn_frame = ttk.Frame(root, padding=(10, 0, 10, 10))
    btn_frame.pack(fill=tk.X)
    ttk.Button(btn_frame, text="選択した項目を削除", command=delete).pack(side=tk.LEFT)
    ttk.Label(btn_frame, text="変更は自動保存されます", foreground="gray").pack(side=tk.RIGHT)

    root.mainloop()


if __name__ == "__main__":
    main()
