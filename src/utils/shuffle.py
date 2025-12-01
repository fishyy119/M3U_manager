import math
import random
from typing import List


def path_tree_similarity(p1_parts: List[str], p2_parts: List[str], alpha: float = 0.5, max_distance: int = 4) -> float:
    """
    基于树距离的路径相似度。
    - 找最近公共祖先（LCA）深度
    - 树距离 = (len1 - lca_depth) + (len2 - lca_depth)
    - 相似度 = exp(-alpha * distance)

    Args:
        p1_parts: 文件1的路径部分
        p2_parts: 文件2的路径部分
        alpha: 控制距离衰减强度
        max_distance: 截断距离阈值，避免指数膨胀

    Returns:
        float: 相似度的倒数，可以直接用于随机抽取的排斥权重
    """
    lca_depth = 0
    for a, b in zip(p1_parts, p2_parts):
        if a == b:
            lca_depth += 1
        else:
            break

    # 树距离，不考虑最后一段到文件的距离
    # 同目录文件距离为0, 同系列歌曲的典型值设定为2
    distance = (len(p1_parts) - lca_depth) + (len(p2_parts) - lca_depth)
    clamped_distance = min(max_distance, distance)

    # 相似度的倒数
    weight = math.exp(alpha * clamped_distance)
    return weight


def weighted_fisher_yates_index(paths: List[str]) -> List[int]:
    """
    基于加权 Fisher-Yates 生成排序后的索引列表。
    alpha 越大 → 越排斥路径相似的歌曲连续出现
    """
    n = len(paths)
    path_parts_list = [p.replace("\\", "/").split("/")[:-1] for p in paths]
    # 初始化索引列表
    idx = list(range(n))

    # 从右向左逐步确定位置
    for i in range(n - 1, 0, -1):
        if i == n - 1:
            # 最右边，均匀随机
            j = random.randint(0, i)
        else:
            last_idx = idx[i + 1]

            # 动态惩罚系数，用于在候选空间缩小时保证惩罚效果
            # exp(-0.5) = 0.606, exp(-1) = 0.3678
            alpha = 0.5 * (1 + math.exp(-0.05 * i))

            # 计算权重
            weights = [
                path_tree_similarity(path_parts_list[idx[j]], path_parts_list[last_idx], alpha=alpha)
                for j in range(i + 1)
            ]

            # 带权重随机抽取 j
            j = random.choices(range(i + 1), weights=weights, k=1)[0]

        # **直接在索引列表中交换**
        idx[i], idx[j] = idx[j], idx[i]

    return idx
