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
        self.song_listbox.configure(activestyle='none')
        self.song_listbox.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # 按钮：刷新
        browse_button = tk.Button(root, text="Browse", command=self.browse_directory)
        browse_button.pack(side=tk.BOTTOM, padx=10, pady=10)
        
        # 按钮：创建新m3u文件
        self.open_child_window_button = tk.Button(self.root, text="创建新m3u文件", command=self.open_merge_m3u_window)
        self.open_child_window_button.pack(padx=10, pady=10)
        
        # 按钮：打乱播放列表
        shuffle_button = tk.Button(root, text="Shuffle", command=self.shuffle_playlist)
        shuffle_button.pack(side=tk.BOTTOM, padx=10, pady=(0, 10))
        
        # 按钮：播放列表去重
        deduplicate_button = tk.Button(root, text="Deduplicate", command=self.deduplicate_playlist)
        deduplicate_button.pack(side=tk.BOTTOM, padx=10, pady=(0, 10))
        
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

    def shuffle_playlist(self):
        # 打乱选中的播放列表
        files = self.m3u_listbox.curselection()
        if files:
            for index in files:
                playlist_file = self.m3u_path_list[index]
                playlist = []
                with open(playlist_file, "r", encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            playlist.append(line)
                list_index = list(range(len(playlist)))
                random.shuffle(list_index)  # 对索引打乱，写入时直接映射
                with open(playlist_file, "w", encoding='utf-8') as f:
                    for index in list_index:
                        f.write(f"{playlist[index]}\n")
            # 重新加载播放列表文件
            self.load_playlist_files()
        else:
            tk.messagebox.showerror("Error", "没有指定m3u文件")
            
    def deduplicate_playlist(self):
        # 去重选中的播放列表
        files = self.m3u_listbox.curselection()
        if files:
            for index in files:
                playlist_file = self.m3u_path_list[index]
                with open(playlist_file, "r", encoding='utf-8') as f:
                    lines = f.readlines()
                lines_set = set(lines)
                with open(playlist_file, "w", encoding='utf-8') as f:
                    for line in lines_set:
                        f.write(line)
            # 重新加载播放列表文件
            self.load_playlist_files()
        else:
            tk.messagebox.showerror("Error", "没有指定m3u文件")
            
    def browse_directory(self):
        # 浏览并加载新的播放列表文件
        self.load_playlist_files()

if __name__ == "__main__":
    # 创建 Tkinter 窗口，并启动应用程序
    root = tk.Tk()
    app = M3UMManagerApp(root)
    root.mainloop()
