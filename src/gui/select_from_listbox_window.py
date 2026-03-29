import tkinter as tk
from typing import Callable, List, Optional


class SelectFromListboxWindow:
    """
    通用选择窗口：用于在多个候选项中选择一个。
        - parent: 父窗口
        - candidates: 候选项（字符串列表）
        - on_confirm: 确认回调，参数为所选索引（int），未选择则为None
    """

    def __init__(self, parent: tk.Tk, candidates: List[str], on_confirm: Callable[[Optional[int]], None]):
        self.parent = parent
        self.candidates = candidates
        self.on_confirm = on_confirm
        self.top = tk.Toplevel(parent)
        self.top.title("请选择候选路径")
        self.top.grab_set()
        self.top.minsize(350, 300)
        self.top.resizable(False, False)

        self.listbox = tk.Listbox(self.top, selectmode=tk.SINGLE, width=50, height=15, borderwidth=0.5, relief="solid")
        self.listbox.configure(activestyle="none", exportselection=False, selectbackground="green")
        for item in candidates:
            self.listbox.insert(tk.END, item)
        self.listbox.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        self.ok_button = tk.Button(self.top, text="确定", command=self._on_ok, width=10)
        self.cancel_button = tk.Button(self.top, text="取消", command=self._on_cancel, width=10)
        self.ok_button.grid(row=1, column=0, sticky="ew", padx=(10, 5), pady=(0, 10))
        self.cancel_button.grid(row=1, column=1, sticky="ew", padx=(5, 10), pady=(0, 10))

        self.listbox.bind("<Double-1>", lambda e: self._on_ok())
        self.top.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _on_ok(self):
        selection = self.listbox.curselection()
        if selection:
            self.on_confirm(selection[0])
        else:
            self.on_confirm(None)
        self.top.destroy()

    def _on_cancel(self):
        self.on_confirm(None)
        self.top.destroy()
