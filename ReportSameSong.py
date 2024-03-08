import os
import json
from LoadFileTree import SettingLoader

def scan_file_tree(node: dict,
                   search_result: dict,
                   path: str
                   ) -> int:
    for name, new_node in node.items():
            if isinstance(new_node, dict):  # 如果是目录节点
                new_path = path + "\\" + name  # 用于规避引用传递
                scan_file_tree(new_node, search_result, new_path)
            else:  # 如果是文件节点
                if path[0] == "\\":  # 取出首位反斜杠
                    path = path[1:]
                path_list = search_result.setdefault(name + new_node, [])  # 以列表存储此歌曲的所有存在路径
                path_list.append(path)

def search_same_file(search_result: dict) -> None:
    for song in list(search_result.keys()):
        if len(search_result[song]) <= 1:
            del search_result[song]

if __name__ == "__main__":
    setting_loader = SettingLoader('setting.json')
    settings = setting_loader.read_settings()
    root_dir = settings['root_dir']  # 音乐库文件
    search_result = {}  

    try:
        with open('file_tree.json', 'r', encoding='utf-8') as f:
            file_tree = json.load(f)
    except FileNotFoundError:
        print('请首先运行"LoadFileTree.py"获取file_tree文件')
        exit()

    scan_file_tree(file_tree, search_result, '')
    search_same_file(search_result)
    count_same = len(search_result)
    with open('report_same_song.json', 'w', encoding='utf-8') as f:
        print(f"在音乐库中发现{count_same}个重复项")
        f.write(json.dumps(search_result, ensure_ascii=False, indent=4))

