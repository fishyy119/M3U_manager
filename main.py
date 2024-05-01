import os
import random
import json
import tkinter as tk
from tkinter import filedialog
from SettingLoader import SettingLoader
from MergeM3UWindow import MergeM3UWindow


class M3UMManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("M3U Manager")
        self.setting_loader = SettingLoader("setting.json")
        self.settings = self.setting_loader.read_settings()
        
        # 存储m3u文件的路径(与m3u_listbox同序)
        self.m3u_path_list = []
        
        # 列表框：m3u列表
        self.m3u_listbox = tk.Listbox(root, width=60, height=30)
        # 无下划线 失去焦点选中不变 选中颜色
        self.m3u_listbox.configure(activestyle='none', exportselection=False, selectbackground='green')
        self.m3u_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.m3u_listbox.bind("<<ListboxSelect>>", self.show_selected_playlist)
        
        # 列表框：歌曲
        self.song_listbox = tk.Listbox(root, width=60, height=30)
        self.song_listbox.configure(activestyle='none', exportselection=False, selectbackground='green')
        self.song_listbox.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Frame：容纳刷新、创建两个按钮
        refresh_create_frame = tk.Frame(root, bd=2, relief=tk.GROOVE)
        refresh_create_frame.pack(side=tk.BOTTOM, padx=10, pady=10)
        
        # 按钮：刷新
        refresh_button = tk.Button(refresh_create_frame, text="刷新", command=self.refresh_directory)
        refresh_button.grid(row=1, column=1, padx=10, pady=(10,10), ipadx=5, sticky='ew')
        
        # 按钮：创建新m3u文件
        self.open_child_window_button = tk.Button(refresh_create_frame, text="创建新m3u文件", command=self.open_merge_m3u_window)
        self.open_child_window_button.grid(row=1, column=2, padx=10, pady=(10,10), ipadx=5, sticky='ew')
        
        # Frame：容纳打乱、去重、上移、下移、置顶、删除六个按钮
        editm3u_frame = tk.Frame(root, bd=2, relief=tk.GROOVE)
        editm3u_frame.pack(side=tk.TOP, padx=10, pady=10)
        label = tk.Label(editm3u_frame, text="操作右侧列表：")
        label.grid(row=1, column=1, columnspan=4, pady=(0,10))
        
        # 按钮：打乱播放列表
        shuffle_button = tk.Button(editm3u_frame, text="随机打乱", command=self.shuffle_playlist)
        shuffle_button.grid(row=3, column=1, columnspan=2, padx=10, pady=(0,10), ipadx=5, sticky='ew')
        
        # 按钮：播放列表去重
        deduplicate_button = tk.Button(editm3u_frame, text="去除重复项", command=self.deduplicate_playlist)
        deduplicate_button.grid(row=3, column=3, columnspan=2, padx=10, pady=(0,10), ipadx=5, sticky='ew')
        
        # 按钮：对列表中歌曲的上移、下移、置顶、删除
        self.btn_move_up = tk.Button(editm3u_frame, text="上移", command=self.move_up)
        self.btn_move_up.grid(row=2, column=1, padx=5, pady=10, ipadx=5)
        
        self.btn_move_down = tk.Button(editm3u_frame, text="下移", command=self.move_down)
        self.btn_move_down.grid(row=2, column=2, padx=5, pady=10, ipadx=5)
        
        self.btn_move_top = tk.Button(editm3u_frame, text="置顶", command=self.move_top)
        self.btn_move_top.grid(row=2, column=3, padx=5, pady=10, ipadx=5)
        
        self.btn_delete = tk.Button(editm3u_frame, text="删除", command=self.delete)
        self.btn_delete.grid(row=2, column=4, padx=5, pady=10, ipadx=5)
        
        # 加载播放列表文件
        self.load_playlist_files()

    def load_playlist_files(self):
        # 从设置中读取播放列表目录
        if self.settings:
            directory = self.settings.get("m3u_directory")
            if directory:
                self.playlist_directory = directory
                
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

    def open_merge_m3u_window(self):
        self.merge_m3u_window = MergeM3UWindow(self.root, self.m3u_path_list, self.settings.get("m3u_directory"))
        # 用以解决弹出警告窗口后该窗口被销毁的问题
        self.merge_m3u_window.top.wait_window()

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
            list_index = list(set(list_index))
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
            
    def refresh_directory(self):
        # 刷新播放列表
        self.load_playlist_files()

if __name__ == "__main__":
    # 创建 Tkinter 窗口，并启动应用程序
    root = tk.Tk()
    app = M3UMManagerApp(root)
    root.mainloop()
