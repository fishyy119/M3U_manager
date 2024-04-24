import os
import json
from SettingLoader import SettingLoader
from FileTreeMatcher import FileTreeMatcher
'''
搜索黑名单中歌曲在m3u及音乐库中位置
搜索report_not_found.json中歌曲在m3u中位置
'''

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

def get_targe() -> list:
    while True:
        try:
            target_int = int(input("请输入:\n1:搜素setting.json中黑名单歌曲\n2:搜索report_not_found.json中歌曲\n"))
            if target_int == 1:
                target = black_song
                break
            elif target_int == 2:
                with open('report_not_found.json', 'r', encoding='utf-8') as f:
                    song_not_found = list(json.load(f))
                target = song_not_found
                break
            else:
                print("只能为1或2，重新输入")
                continue
        except FileNotFoundError:
            print("不存在report_not_found.json，请先运行ReportSongNotFound.py")
            exit()
        except ValueError as e:
            print(f"{e} 重新输入")
            continue
    return target

if __name__ == "__main__":
    setting_loader = SettingLoader('setting.json')
    settings = setting_loader.read_settings()
    root_dir = settings['root_dir']  # 音乐库文件
    m3u_directory = settings['m3u_directory']  # m3u存储路径
    white_extension = settings['white_extension']  # 音乐后缀名识别
    black_song = settings['black_song']  # 跳过匹配的歌曲黑名单
    
    # 更新并加载文件树
    file_tree_matcher = FileTreeMatcher(root_dir, white_extension, black_song)
    file_tree_matcher.build_file_tree()
    file_tree_matcher.save_to_json("file_tree.json")
    with open('file_tree.json', 'r', encoding='utf-8') as f:
        file_tree = json.load(f)

    search_result = {'search_in_filetree': {}, 'search_in_m3u': {}}  # 两处搜索结果存储于同一个字典
    
    songs = get_targe()  # 获取搜索目标

    count_filetree = find_file_in_tree(file_tree, search_result['search_in_filetree'], '', [0], songs)
    count_m3u = find_file_in_m3u(m3u_directory, search_result['search_in_m3u'], songs)
    with open('report_search_song.json', 'w', encoding='utf-8') as f:
        print(f"在音乐库中发现{count_filetree}个匹配项，在m3u文件中发现{count_m3u}个匹配项")
        f.write(json.dumps(search_result, ensure_ascii=False, indent=4))

    