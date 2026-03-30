"""
调用 Nuitka 编译为可执行文件

依赖：
    - Nuitka: 2.8.4
"""

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def calculate_src_hash(src_dir: Path) -> str:
    """计算src目录下所有文件的SHA256哈希值，包括空白符变化。"""
    hash_obj = hashlib.sha256()
    for file_path in sorted(src_dir.rglob("*")):
        if file_path.is_file():
            with open(file_path, "rb") as f:
                hash_obj.update(f.read())
    return hash_obj.hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Build M3U Manager executable")
    parser.add_argument("--force", "-f", action="store_true", help="Force recompilation even if hash unchanged")

    args = parser.parse_args()
    force: bool = args.force

    src_dir = ROOT / "src"
    cache_file = Path(".build_cache")
    current_hash = calculate_src_hash(src_dir)

    if cache_file.exists():
        with open(cache_file, "r") as f:
            cached_hash = f.read().strip()
    else:
        cached_hash = None

    if cached_hash == current_hash and not force and Path("M3U Manager.exe").exists():
        print("Source code unchanged, skipping compilation. Use --force to override.")
        return

    nuitka_cmd = [sys.executable, "-m", "nuitka"]
    nuitka_args = [
        "--standalone",
        "--onefile",
        "--windows-console-mode=disable",
        "--enable-plugin=tk-inter",
        # UPX压缩使用参数，加载时间翻倍，体积压缩效果不明显
        # "--onefile-no-compression",
        # "--enable-plugin=upx",
        f"--windows-icon-from-ico={ROOT / 'assets/favicon.ico'}",
        "--product-name=M3U Manager",
        "--product-version=0.2.0",
        "--file-version=0.2.0",
        "--file-description=A simple tool for managing m3u playlists",
        "--output-filename=M3U Manager.exe",
        str(ROOT / "main.py"),
    ]

    subprocess.run(nuitka_cmd + nuitka_args, check=True)

    # 更新缓存
    with open(cache_file, "w") as f:
        f.write(current_hash)


if __name__ == "__main__":
    main()
# 测试加载时间 Measure-Command {Start-Process '.\M3U Manager.exe' -Wait}
