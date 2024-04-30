import os
import tkinter as tk
from tkinter import filedialog
from SettingLoader import SettingLoader
import json

class M3UMManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("M3U Manager")
        self.setting_loader = SettingLoader("setting.json")
        self.settings = self.setting_loader.read_settings()
        
        # 存储m3u文件的路径(与m3u_listbox同序)
        self.m3u_path_list = []
        
        # 创建m3u文件列表框
        self.m3u_listbox = tk.Listbox(root, width=60, height=30)
        # 无下划线 失去焦点选中不变 选中颜色
        self.m3u_listbox.configure(activestyle='none', exportselection=False, selectbackground='green')
        self.m3u_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.m3u_listbox.bind("<<ListboxSelect>>", self.show_selected_playlist)
        
        # 创建歌曲列表框
        self.song_listbox = tk.Listbox(root, width=60, height=30)
        self.song_listbox.configure(activestyle='none')
        self.song_listbox.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # 创建浏览按钮
        browse_button = tk.Button(root, text="Browse", command=self.browse_directory)
        browse_button.pack(side=tk.BOTTOM, padx=10, pady=10)
        
        # 加载播放列表文件
        self.load_playlist_files()

    def load_playlist_files(self):
        # 从设置中读取播放列表目录
        if self.settings:
            directory = self.settings.get("m3u_directory")
            if directory:
                self.playlist_directory = directory
                self.m3u_listbox.delete(0, tk.END)
                # 遍历目录及其子目录下的所有文件，将 .m3u 文件添加到文件列表框中
                for root, _, files in os.walk(directory):
                    for file in files:
                        if file.endswith(".m3u"):
                            self.m3u_listbox.insert(tk.END, file)
                            self.m3u_path_list.append(os.path.join(root, file))

    def show_selected_playlist(self, event):
        # 当用户选择播放列表文件时，显示该文件中的歌曲列表
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            playlist_file = self.m3u_path_list[index]
            self.song_listbox.delete(0, tk.END)
            # 从选定的 .m3u 文件中读取歌曲列表，并在歌曲列表框中显示
            with open(playlist_file, "r", encoding='utf8') as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        self.song_listbox.insert(tk.END, os.path.basename(line))

    def browse_directory(self):
        # 浏览并加载新的播放列表文件
        self.load_playlist_files()

if __name__ == "__main__":
    # 创建 Tkinter 窗口，并启动应用程序
    root = tk.Tk()
    app = M3UMManagerApp(root)
    root.mainloop()
