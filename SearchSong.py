import os
import json
from LoadFileTree import SettingLoader

def find_file_in_m3u(m3u_directory: str,
                     search_result: dict,
                     target: list
                     ) -> int:
    count = 0
    for filename in os.listdir(m3u_directory):
        if filename.endswith(".m3u"):
            file_path = os.path.join(m3u_directory, filename)
            with open(file_path, "r", encoding='utf-8') as f:
                m3u_name = os.path.basename(file_path)
                for line in f:
                    line = line.strip()
                    if line:
                        song_name = os.path.basename(line)
                        if song_name in target:
                            m3u_list = search_result.setdefault(song_name, [])  # 以列表存储此歌曲的所有存在m3u
                            m3u_list.append(m3u_name)
                            count = count + 1
    return count

def find_file_in_tree(node: dict,
                      search_result: dict,
                      path: str,
                      count: list,  # 初次调用时定义为[0]以进行引用传递
                      target: list
                      ) -> int:
    for name, new_node in node.items():
            if isinstance(new_node, dict):  # 如果是目录节点
                new_path = path + "\\" + name  # 用于规避引用传递
                find_file_in_tree(new_node, search_result, new_path, count, target)
            else:  # 如果是文件节点
                if name + new_node in target:  # 匹配
                    if path[0] == "\\":  # 取出首位反斜杠
                        path = path[1:]
                    path_list = search_result.setdefault(name + new_node, [])  # 以列表存储此歌曲的所有存在路径
                    path_list.append(path)
                    count[0] = count[0] + 1
    return count[0]

if __name__ == "__main__":
    setting_loader = SettingLoader('setting.json')
    settings = setting_loader.read_settings()
    songs = settings['black_song']  # 计划搜索的歌曲名（带后缀），此处为搜索黑名单
    root_dir = settings['root_dir']  # 音乐库文件
    m3u_directory = settings['m3u_directory']  # m3u存储路径
    search_result = {'search_in_filetree': {}, 'search_in_m3u': {}}  # 两处搜索结果存储于同一个字典

    try:
        with open('file_tree.json', 'r', encoding='utf-8') as f:
            file_tree = json.load(f)
    except FileNotFoundError:
        print('请首先运行"LoadFileTree.py"获取file_tree文件')
        exit()

    count_filetree = find_file_in_tree(file_tree, search_result['search_in_filetree'], '',[0], songs)
    count_m3u = find_file_in_m3u(m3u_directory, search_result['search_in_m3u'], songs)
    with open('report_search_song.json', 'w', encoding='utf-8') as f:
        print(f"在音乐库中发现{count_filetree}个匹配项，在m3u文件中发现{count_m3u}个匹配项")
        f.write(json.dumps(search_result, ensure_ascii=False, indent=4))

    