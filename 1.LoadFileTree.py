import os
import json
from SettingLoader import SettingLoader
from FileTreeMatcher import FileTreeMatcher
'''
todo:
'''
    

if __name__ == "__main__":
    setting_loader = SettingLoader('setting.json')
    settings = setting_loader.read_settings()
    root_dir = settings['root_dir']  # 音乐库文件
    m3u_directory = settings['m3u_directory']  # m3u存储路径
    white_extension = settings['white_extension']  # 音乐后缀名识别
    black_list_state = settings['black_list_state']  # 黑名单开关
    if black_list_state:
        black_song = settings['black_song']  # 跳过匹配的歌曲黑名单
    else:
        black_song = []

    file_tree_matcher_old = FileTreeMatcher(root_dir, white_extension, black_song)
    file_tree_matcher_old.build_file_tree_from_m3u(m3u_directory)
    file_tree_matcher_old.save_to_json("file_tree_m3u.json")

    file_tree_matcher = FileTreeMatcher(root_dir, white_extension, black_song)
    file_tree_matcher.build_file_tree()
    file_tree_matcher.save_to_json("file_tree.json")

    match_map = file_tree_matcher.get_path_mapping(file_tree_matcher_old.file_tree)
    with open('map.json', 'w', encoding='utf-8') as f:
        print(f"匹配完毕，共匹配到{len(match_map)}项")
        f.write(json.dumps(match_map, ensure_ascii=False, indent=4))
    