import datetime
import math
from pathlib import Path
from typing import List

from line_profiler import LineProfiler

import src.utils.shuffle as shuffle
from src.utils.shuffle import weighted_fisher_yates_index


def test_main():
    for alpha in [0.5, 1.0, 1.5]:
        for d in range(5):
            print(f"alpha={alpha}, distance={d}, weight={math.exp(alpha * d)}")

    m3u_path = r"C:\Users\zj\Music\Dopamine\!新建列表.m3u"
    playlist: List[str] = []
    with open(m3u_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                playlist.append(line)

    weighted_fisher_yates_index(playlist)


if __name__ == "__main__":
    lp = LineProfiler()
    lp.add_module(shuffle)

    lp_wrapper = lp(test_main)
    lp_wrapper()
    timestamp = datetime.datetime.now().strftime("%H%M%S")
    name = Path(__file__).stem
    short_name = "_".join(name.split("_")[:2])  # 取前两个单词组合
    profile_filename = f"profile_{short_name}_{timestamp}.txt"
    with open(profile_filename, "w", encoding="utf-8") as f:
        lp.print_stats(sort=True, stream=f)
