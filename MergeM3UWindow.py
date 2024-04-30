import tkinter as tk
import os


class MergeM3UWindow:
    """
    子窗口：由已有m3u文件生成新m3u文件
    """
    def __init__(self, parent, m3u_path_list, m3u_directory):
        self.parent = parent
        self.m3u_path_list = m3u_path_list
        self.m3u_directory = m3u_directory
        self.top = tk.Toplevel(parent)
        self.top.title("生成M3U文件")
        self.top.grab_set()  # 保持顶端

        # 创建列表框(选择m3u)
        self.listbox = tk.Listbox(self.top, selectmode=tk.MULTIPLE, width=30, height=25, borderwidth=0.5, relief="solid")
        self.listbox.configure(activestyle='none', exportselection=False, selectbackground='green')
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.show_m3u()

        # 创建输入框(新m3u文件名称)
        self.entry = tk.Entry(self.top, width=30, borderwidth=0.5, relief="solid")
        self.entry.insert(0, '!新建列表.m3u')
        self.entry.pack(fill=tk.X, padx=10, pady=(0, 10))

        # 创建按钮(生成)
        self.button = tk.Button(self.top, text="生成M3U", command=self.generate_m3u, borderwidth=1, relief='raised')
        self.button.pack(fill=tk.X, padx=10, pady=(0, 10))
        
    def show_m3u(self):
        self.listbox.delete(0, tk.END)
        for f in self.m3u_path_list:
            self.listbox.insert(tk.END, os.path.basename(f))

    def generate_m3u(self):
        # 生成新的 m3u 文件
        files = self.listbox.curselection()  # 索引元组
        if files:
            output_name = self.entry.get().strip()
            if output_name:
                with open(os.path.join(self.m3u_directory, output_name), "w", encoding='utf-8') as f:
                    for index in files:
                        # 需要保证listbox与m3u_path_list的同序
                        m3u_file = self.m3u_path_list[index]
                        with open(m3u_file, "r", encoding='utf-8') as m3u:
                            for line in m3u:
                                f.write(line)
                self.top.destroy()
            else:
                tk.messagebox.showerror("Error", "需输入有效文件名")
        else:
            tk.messagebox.showerror("Error", "需选择文件")

