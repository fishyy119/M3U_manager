import argparse
import json
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path

from src.gui.m3u_manager_app import M3UManagerApp


@dataclass
class Args:
    m3u_dir: Path
    library_root: list[Path]
    select_m3u_name: str | None = None

    @classmethod
    def from_ns(cls, ns: argparse.Namespace) -> "Args":
        # 自动补全 .m3u 后缀
        if ns.select_m3u and not ns.select_m3u.endswith(".m3u"):
            ns.select_m3u += ".m3u"

        # 如果缺失 m3u_dir 或 library_root，则从 settings.json 读取
        if not ns.m3u_dir or not ns.library_root:
            settings_path = Path("settings.json")
            if settings_path.exists():
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                if not ns.m3u_dir:
                    ns.m3u_dir = settings.get("m3u_dir")
                if not ns.library_root:
                    ns.library_root = settings.get("library_root", [])
            else:
                raise ValueError("m3u_dir or library_root not provided and settings.json not found")

        # 转为 Path 对象
        library_paths = [Path(p) for p in ns.library_root]
        m3u_dir_path = Path(ns.m3u_dir)

        return cls(
            library_root=library_paths,
            m3u_dir=m3u_dir_path,
            select_m3u_name=ns.select_m3u,
        )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="M3U Manager Application")
    p.add_argument("--m3u_dir", "-d", type=str, help="指定M3U目录")
    p.add_argument("--library_root", "-l", type=str, nargs="+", help="指定库根目录")
    p.add_argument("--select-m3u", "-s", type=str, help="预先选定m3u文件名，打开后自动选中该文件")

    args = Args.from_ns(p.parse_args())

    root = tk.Tk()
    app = M3UManagerApp(
        root,
        library_root=args.library_root,
        m3u_directory=args.m3u_dir,
        pre_select=args.select_m3u_name,
    )
    app.run()
