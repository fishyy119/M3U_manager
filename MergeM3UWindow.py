import tkinter as tk
import os


class MergeM3UWindow:
    """
    子窗口：由已有m3u文件生成新m3u文件
        parent：
            父窗口（即主窗口）
        m3u_path_list：
            所有m3u的路径
        m3u_directory：
            新创建的m3u的根目录
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
        
        self.show_m3u()

        # 创建输入框(新m3u文件名称)
        self.entry = tk.Entry(self.top, width=30, borderwidth=0.5, relief="solid")
        self.entry.insert(0, '!新建列表.m3u')

        # 创建按钮(生成)
        self.button = tk.Button(self.top, text="生成M3U", command=self.generate_m3u, borderwidth=1, relief='raised')
        
        
        ############################################################################
        # 布局
        self.top.minsize(250, 300)
        self.top.grid_rowconfigure(0, weight=1)
        self.top.grid_columnconfigure(0, weight=1)
        
        self.listbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.entry.grid(row=1, column=0, sticky="ew", padx=10)
        self.button.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        ############################################################################
        
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
                songs = []
                for index in files:
                    # 需要保证listbox与m3u_path_list的同序
                    m3u_file = self.m3u_path_list[index]
                    with open(m3u_file, "r", encoding='utf-8') as m3u:
                        for line in m3u:
                            songs.append(line)
                with open(os.path.join(self.m3u_directory, output_name), "w", encoding='utf-8') as f:
                    for song in songs:
                        f.write(song)
                        
                self.top.destroy()
            else:
                tk.messagebox.showerror("Error", "需输入有效文件名")
        else:
            tk.messagebox.showerror("Error", "需选择文件")

