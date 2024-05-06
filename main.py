import os
import random
import json
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from SettingLoader import SettingLoader
from MergeM3UWindow import MergeM3UWindow
"""
todo:
    关于SettingLoader的窗口化适配
    设置界面
    整合12345
"""

class M3UMManagerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("M3U Manager")
        # self.root.iconbitmap('img/favicon.ico')
        self.setting_loader = SettingLoader("setting.json")
        self.settings = self.setting_loader.read_settings()
        
        ############################################################################
        # Frame：显示信息
        info_frame = tk.Frame(root, bd=2, relief=tk.GROOVE)
        
        self.m3u_info = tk.Label(info_frame)
        self.playlist_info = tk.Label(info_frame)
        
        self.m3u_info.pack()  # m3u个数
        self.playlist_info.pack()  # 歌曲个数
        
        ############################################################################
        # Frame：容纳刷新、删除、创建、重命名
        refresh_create_frame = tk.Frame(root, bd=2, relief=tk.GROOVE)
        
        refresh_button = tk.Button(refresh_create_frame, text="刷新", command=self.refresh_directory)
        delete_m3u_button = tk.Button(refresh_create_frame, text="删除m3u", command=self.delete_m3u)
        rename_m3u_button = tk.Button(refresh_create_frame, text="重命名m3u", command=self.rename_m3u)
        self.open_child_window_button = tk.Button(refresh_create_frame, text="创建m3u", command=self.open_merge_m3u_window)
        
        refresh_create_frame.grid_columnconfigure(0, weight=1)
        refresh_create_frame.grid_columnconfigure(1, weight=1)
        
        refresh_button.grid(row=0, column=0, padx=10, pady=5, sticky='ew')  # 刷新
        delete_m3u_button.grid(row=0, column=1, padx=10, pady=5, sticky='ew')  # 删除m3u
        rename_m3u_button.grid(row=1, column=0, padx=10, pady=5, sticky='ew')  # 重命名m3u
        self.open_child_window_button.grid(row=1, column=1, padx=10, pady=5, sticky='ew')  # 创建新m3u文件
        
        ############################################################################
        # Frame：容纳打乱、去重、上移、下移、置顶、删除六个按钮
        editm3u_frame = tk.Frame(root, bd=2, relief=tk.GROOVE, width=40)
        
        label = tk.Label(editm3u_frame, text="操作右侧列表：")
        shuffle_button = tk.Button(editm3u_frame, text="随机打乱", command=self.shuffle_playlist)
        deduplicate_button = tk.Button(editm3u_frame, text="去除重复项", command=self.deduplicate_playlist)
        btn_move_up = tk.Button(editm3u_frame, text="上移", command=self.move_up)
        btn_move_down = tk.Button(editm3u_frame, text="下移", command=self.move_down)
        btn_move_top = tk.Button(editm3u_frame, text="置顶", command=self.move_top)
        btn_delete = tk.Button(editm3u_frame, text="删除", command=self.delete)
        
        label.grid(row=1, column=1, columnspan=4, pady=(2,5))
        shuffle_button.grid(row=3, column=1, columnspan=2, padx=10, pady=(0,10), ipadx=5, sticky='ew')  # 随机打乱
        deduplicate_button.grid(row=3, column=3, columnspan=2, padx=10, pady=(0,10), ipadx=5, sticky='ew')  # 去重
        btn_move_up.grid(row=2, column=1, padx=5, pady=10, ipadx=5)  # 上移
        btn_move_down.grid(row=2, column=2, padx=5, pady=10, ipadx=5)  # 下移
        btn_move_top.grid(row=2, column=3, padx=5, pady=10, ipadx=5)  # 置顶
        btn_delete.grid(row=2, column=4, padx=5, pady=10, ipadx=5)  # 删除
        
        ############################################################################
        # Lisbbox相关 
        # 存储m3u文件的路径(与m3u_listbox同序)
        self.m3u_path_list = []
        
        # 列表框：m3u列表
        self.m3u_listbox = tk.Listbox(root, width=60, height=30)
        # 无下划线 失去焦点选中不变 选中颜色
        self.m3u_listbox.configure(activestyle='none', exportselection=False, selectbackground='green')
        self.m3u_listbox.bind("<<ListboxSelect>>", self.show_selected_playlist)
        
        # 列表框：歌曲
        self.song_listbox = tk.Listbox(root, width=60, height=30)
        self.song_listbox.configure(activestyle='none', exportselection=False, selectbackground='green')
        
        ############################################################################
        # 主窗口布局
        self.root.minsize(600, 400)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        # 对于中间的按钮列，该行留空
        # 此行用于吸收纵向的多余空间
        self.root.grid_rowconfigure(2, weight=1)  
        
        self.m3u_listbox.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=10, pady=10)
        self.song_listbox.grid(row=0, column=2, rowspan=4, sticky="nsew", padx=10, pady=10)
        info_frame.grid(row=0, column=1, sticky='ew', padx=10, pady=10)
        editm3u_frame.grid(row=1, column=1, sticky='ew', padx=10, pady=10)
        refresh_create_frame.grid(row=3, column=1, rowspan=2, sticky='ews', padx=10, pady=10)
        ############################################################################
        # 添加超链接
        link_m3u_label = tk.Label(self.root, text="打开m3u库", fg="blue", cursor="hand2")
        link_playlist_label = tk.Label(self.root, text="打开m3u文件", fg="blue", cursor="hand2")
        link_m3u_label.bind("<Button-1>", self.open_m3u_folder)
        link_playlist_label.bind("<Button-1>", self.open_playlist)
        
        link_m3u_label.grid(row=4, column=0, padx=10, pady=(0,4), sticky="nw")
        link_playlist_label.grid(row=4, column=2, padx=10, pady=(0,4), sticky="ne")
        ############################################################################
        
        # 加载m3u文件
        self.load_playlist_files()

    def load_playlist_files(self):
        # 从设置中读取播放列表目录
        if self.settings:
            directory = self.settings.get("m3u_directory")
            if directory:
                self.playlist_directory = directory
                self.m3u_path_list.clear()  # 清空
                
                # 记录当前选中项（如果未选择则默认第一项）
                selection_index = self.m3u_listbox.curselection()
                if not selection_index:
                    selection_index = (0,)
                
                self.m3u_listbox.delete(0, tk.END)
                # 遍历目录及其子目录下的所有文件，将 .m3u 文件添加到文件列表框中
                for root, _, files in os.walk(directory):
                    for file in files:
                        if file.endswith(".m3u"):
                            self.m3u_listbox.insert(tk.END, file)
                            self.m3u_path_list.append(os.path.join(root, file))
                self.m3u_info.config(text=f"m3u文件总数：{len(self.m3u_path_list)}")
                
                # 设置选中的索引
                self.m3u_listbox.selection_set(selection_index)
                self.show_selected_playlist()

    def show_selected_playlist(self, event=None):
        # 当用户选择播放列表文件时，显示该文件中的歌曲列表
        selection = self.m3u_listbox.curselection()
        if selection:
            index = selection[0]
            playlist_file = self.m3u_path_list[index]
            self.song_listbox.delete(0, tk.END)
            # 从选定的 .m3u 文件中读取歌曲列表，并在歌曲列表框中显示
            with open(playlist_file, "r", encoding='utf8') as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        self.song_listbox.insert(tk.END, os.path.basename(line))
            self.playlist_info.config(text=f"列表内歌曲总数：{self.song_listbox.size()}")

    def edit_m3u(self, m3u_path, operation, index=0):
        """
        对m3u进行操作，包括打乱、去重、上移、下移、置顶、删除
            operation: 
                'shuffle' / 'deduplicate' / 'up' / 'down' / 'top' / 'del'
            index:
                对于后四个，需要操作的序号（单个）
        """
        playlist = []
        with open(m3u_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    playlist.append(line)
                    
        # 先对索引列表输出，最后映射
        list_index = list(range(len(playlist)))
        if operation == 'shuffle':
            random.seed()
            random.shuffle(list_index)
        elif operation == 'deduplicate':
            tmp_playlist = []  # 用于去重
            for i, song in enumerate(playlist):
                if not song in tmp_playlist:
                    tmp_playlist.append(song)
                else:
                    list_index.remove(i)
        elif operation == 'up':
            if index > 0:
                list_index[index - 1] = index
                list_index[index] = index - 1
        elif operation == 'down':
            if index < len(playlist) - 1:
                list_index[index + 1] = index
                list_index[index] = index + 1
        elif operation == 'top':
            del list_index[index]
            list_index.insert(0, index)
        elif operation == 'del':
            del list_index[index]
            
        # 写入m3u
        with open(m3u_path, "w", encoding='utf-8') as f:
            for index in list_index:
                f.write(f"{playlist[index]}\n")
        # 对于打乱和去重，需要重新加载一下
        if operation == 'shuffle' or operation == 'deduplicate':
            self.load_playlist_files()

    def shuffle_playlist(self):
        # 打乱选中的播放列表
        files = self.m3u_listbox.curselection()
        if files:
            m3u_path = self.m3u_path_list[files[0]]
            self.edit_m3u(m3u_path, 'shuffle')
        else:
            tk.messagebox.showerror("Error", "没有指定m3u文件")
            
    def deduplicate_playlist(self):
        # 去重选中的播放列表
        files = self.m3u_listbox.curselection()
        if files:
            m3u_path = self.m3u_path_list[files[0]]
            self.edit_m3u(m3u_path, 'deduplicate')
            self.playlist_info.config(text=f"列表内歌曲总数：{self.song_listbox.size()}")
        else:
            tk.messagebox.showerror("Error", "没有指定m3u文件")
            
    def move_up(self):
        selection = self.song_listbox.curselection()
        m3u_path = self.m3u_path_list[self.m3u_listbox.curselection()[0]]
        if selection:
            i = selection[0]
            # 顶端自然不需要移动
            if i > 0: 
                self.song_listbox.insert(i-1, self.song_listbox.get(i))
                self.song_listbox.delete(i+1)
                self.song_listbox.selection_clear(0, tk.END)
                self.song_listbox.selection_set(i-1)
                self.edit_m3u(m3u_path, 'up', i)
                    
    def move_down(self):
        selection = self.song_listbox.curselection()
        m3u_path = self.m3u_path_list[self.m3u_listbox.curselection()[0]]
        if selection:
            i = selection[0]
            # 末端不需要移动
            if i < self.song_listbox.size() - 1:
                self.song_listbox.insert(i+2, self.song_listbox.get(i))
                self.song_listbox.delete(i)
                self.song_listbox.selection_clear(0, tk.END)
                self.song_listbox.selection_set(i+1)
                self.edit_m3u(m3u_path, 'down', i)
                    
    def move_top(self):
        selection = self.song_listbox.curselection()
        m3u_path = self.m3u_path_list[self.m3u_listbox.curselection()[0]]
        if selection:
            i = selection[0]
            # 顶端不需要移动
            if i > 0:
                self.song_listbox.insert(0, self.song_listbox.get(i))
                self.song_listbox.delete(i+1)
                self.song_listbox.selection_clear(0, tk.END)
                self.song_listbox.selection_set(0)
                self.edit_m3u(m3u_path, 'top', i)
                    
    def delete(self):
        selection = self.song_listbox.curselection()
        m3u_path = self.m3u_path_list[self.m3u_listbox.curselection()[0]]
        if selection:
            for i in reversed(selection):
                self.song_listbox.delete(i)
                self.edit_m3u(m3u_path, 'del', i)
                self.playlist_info.config(text=f"列表内歌曲总数：{self.song_listbox.size()}")
            
    def open_merge_m3u_window(self):
        self.merge_m3u_window = MergeM3UWindow(self.root, self.m3u_path_list, self.settings.get("m3u_directory"))
        # 用以解决弹出警告窗口后该窗口被销毁的问题
        self.merge_m3u_window.top.wait_window()
        self.load_playlist_files()
        
    def refresh_directory(self):
        # 刷新播放列表
        self.load_playlist_files()
        
    def delete_m3u(self):
        # 获取选中的 m3u 文件
        selected_index = self.m3u_listbox.curselection()
        if selected_index:
            # 弹出确认提示框
            result = tk.messagebox.askokcancel("确认删除", "确定要删除选中的 m3u 文件吗？")
            if result:
                # 执行删除操作
                file_to_delete = self.m3u_path_list[selected_index[0]]
                os.remove(file_to_delete)
                # 更新列表框
                self.refresh_directory()
                
    def rename_m3u(self):
        # 重命名m3u文件
        selected_index = self.m3u_listbox.curselection()
        old_path = self.m3u_path_list[selected_index[0]]
        # 弹出对话框，让用户输入新的文件名
        new_name = simpledialog.askstring("重命名", "输入新文件名（无需输入后缀名）：")

        # 检查用户是否点击了取消按钮或没有输入任何内容
        if new_name is None:
            return
        elif not new_name.strip():
            messagebox.showerror("Error", "输入为空")
            return
        
        
        # 构建新的文件路径
        directory = os.path.dirname(old_path)
        new_path = os.path.join(directory, new_name)

        try:
            # 添加.m3u扩展名
            if not new_path.endswith(".m3u"):
                new_path += ".m3u"
                
            # 重命名文件
            os.rename(old_path, new_path)
        except Exception as e:
            messagebox.showerror("Error", f"文件重命名失败：{e}")
            
        self.load_playlist_files()

    def open_m3u_folder(self, event: tk.Event):
        # 打开m3u库文件夹
        event.widget.config(fg='purple4')
        os.system(f"explorer {self.settings['m3u_directory']}")
        
    def open_playlist(self, event: tk.Event):
        # 打开m3u文件
        event.widget.config(fg='purple4')
        file_path = self.m3u_path_list[self.m3u_listbox.curselection()[0]]
        os.startfile(file_path)

if __name__ == "__main__":
    # 创建 Tkinter 窗口，并启动应用程序
    root = tk.Tk()
    app = M3UMManagerApp(root)
    root.mainloop()
