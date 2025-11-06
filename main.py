import argparse
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path

from src.gui.m3u_manager_app import M3UManagerApp

"""
todo:
    关于SettingLoader的窗口化适配
    设置界面
    整合12345
"""


@dataclass
class Args:
    m3u_dir: str | None = None
    select_m3u_name: str | None = None

    def __post_init__(self):
        if self.select_m3u_name and not self.select_m3u_name.endswith(".m3u"):
            self.select_m3u_name += ".m3u"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="M3U Manager Application")
    parser.add_argument("--m3u_dir", "-d", type=str, help="指定M3U目录（会覆盖setting.json中的目录）")
    parser.add_argument("--select-m3u", "-s", type=str, help="预先选定m3u文件名，打开后自动选中该文件")
    arg_namespace = parser.parse_args()
    args = Args(
        m3u_dir=arg_namespace.m3u_dir,
        select_m3u_name=arg_namespace.select_m3u,
    )

    root = tk.Tk()
    app = M3UManagerApp(
        root,
        setting_path=Path("setting.json"),
        m3u_directory=args.m3u_dir,
        pre_select=args.select_m3u_name,
    )
    app.run()
