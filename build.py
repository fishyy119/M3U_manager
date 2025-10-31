"""
调用 Nuitka 编译为可执行文件

依赖：
    - Nuitka: 2.8.4
"""

import os
import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent

nuitka_cmd = [sys.executable, "-m", "nuitka"]
nuitka_args = [
    "--standalone",
    "--onefile",
    "--windows-console-mode=disable",
    "--enable-plugin=tk-inter",
    # UPX压缩使用参数，加载时间翻倍，体积压缩效果不明显
    # "--onefile-no-compression",
    # "--enable-plugin=upx",
    f"--windows-icon-from-ico={project_root / 'assets/favicon.ico'}",
    "--product-name=M3U Manager",
    "--product-version=0.1.1",
    "--file-version=0.1.1",
    "--file-description=A simple tool for managing m3u playlists",
    "--output-filename=M3U Manager.exe",
    str(project_root / "main.py"),
]

subprocess.run(nuitka_cmd + nuitka_args, check=True)
# 测试加载时间 Measure-Command {Start-Process '.\M3U Manager.exe' -Wait}
