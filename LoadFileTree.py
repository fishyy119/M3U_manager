import os
import json

class FileTreeMatcher:
    def __init__(self,
                 root_dir: str,
                 white_extension: list
                 ) -> None:
        self.root_dir = root_dir  # 存储音乐库的根目录
        self.white_extension = white_extension
        self.file_tree = {}

    def build_file_tree(self) -> None:
        for root, dirs, files in os.walk(self.root_dir):
            current_dir = self.file_tree
            relative_path = root[len(self.root_dir):].split(os.path.sep)
            relative_path[0] = self.root_dir  # 0号位永远是根目录

            for dir_name in relative_path:
                current_dir = current_dir.setdefault(dir_name, {})

            for file_name in files:
                file_name_without_extension, extension = os.path.splitext(file_name)
                if extension in self.white_extension:
                    current_dir[file_name_without_extension] = extension

    def build_file_tree_from_m3u(self, 
                                 m3u_directory: str
                                 ) -> None:
        # root_dir存储音乐库的根目录
        # m3u_directory存储m3u文件的目录
        file_paths = []
        for filename in os.listdir(m3u_directory):
            if filename.endswith(".m3u"):
                file_path = os.path.join(m3u_directory, filename)
                with open(file_path, "r", encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            line_without_root_dir = line[len(self.root_dir):]
                            file_paths.append(line_without_root_dir)

        for file_path in file_paths:
            current_dir = self.file_tree
            path_parts = file_path.split(os.path.sep)
            path_parts[0] = self.root_dir  # 将root_dir作放入头部（之前为''），规避分解指令
            for part in path_parts[:-1]:
                current_dir = current_dir.setdefault(part, {})
            song_name, extension = os.path.splitext(path_parts[-1])
            current_dir[song_name] = extension

    def save_to_json(self, 
                     output_file: str
                     ) -> None:
        file_tree_json = json.dumps(self.file_tree, ensure_ascii=False, indent=4)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(file_tree_json)

    def load_from_json(self, 
                       input_file: str
                       ) -> None:
        with open(input_file, 'r', encoding='utf-8') as f:
            self.file_tree = json.load(f)

    def get_path_mapping(self, 
                         old_file_tree: dict
                         ) -> dict:
        path_mapping = {}
        self._compare_file_trees(self.file_tree, old_file_tree, path_mapping, '')
        return path_mapping

    def _compare_file_trees(self, 
                            new_tree: dict, 
                            old_tree: dict, 
                            path_mapping: dict, 
                            new_path: str
                            ) -> None:
        for name, new_node in new_tree.items():
            if isinstance(new_node, dict):  # 如果是目录节点
                new_path_nn = new_path + "\\" + name  # 用于规避引用传递
                self._compare_file_trees(new_node, old_tree, path_mapping, new_path_nn)
            else:  # 如果是文件节点
                old_path, extension = self._find_file_in_tree(name, old_tree, '')
                if old_path is not None:  # 如果在旧文件树中存在相同文件
                    if old_path[0] == "\\":
                        old_path = old_path[1:]  # 前面会多个反斜杠，去掉
                    if new_path[0] == "\\":
                        new_path = new_path[1:]
                        
                    if old_path != new_path:
                        # 只存储路径不存储歌曲文件名会导致意想不到的麻烦
                        path_mapping[os.path.join(old_path, name + extension)] =\
                            os.path.join(new_path, name + extension)

    def _find_file_in_tree(self, 
                           file_name: str, 
                           tree: dict, 
                           old_path: str
                           ) -> str:
        for name, node in tree.items():
            if isinstance(node, dict):
                old_path_oo = old_path + "\\" + name  # 用于规避引用传递
                result1, result2 = self._find_file_in_tree(file_name, node, old_path_oo)
                if result1:
                    return result1, result2
            elif file_name == name:
                return old_path, node  # 此处取出后缀名用于生成map
        return None, None
    
class SettingLoader:
    DEFAULT_SETTINGS = {
        'root_dir': '/path/to/root/directory',
        'm3u_directory': '/path/to/m3u/files',
        'white_extension': ['.mp3', '.wav', '.flac']
    }

    def __init__(self, 
                 filename: str
                 ) -> None:
        self.filename = filename

    def read_settings(self) -> dict:
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except FileNotFoundError:
            print(f"Settings file '{self.filename}' not found. Creating default settings.")
            settings = self.DEFAULT_SETTINGS
            self.save_settings(settings)
        return settings

    def save_settings(self, 
                      settings: dict
                      ) -> None:
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)

if __name__ == "__main__":
    setting_loader = SettingLoader('setting.json')
    settings = setting_loader.read_settings()
    root_dir = settings['root_dir']  # 音乐库文件
    m3u_directory = settings['m3u_directory']  # m3u存储路径
    white_extension = settings['white_extension']  # 音乐后缀名识别

    file_tree_matcher_old = FileTreeMatcher(root_dir, white_extension)
    file_tree_matcher_old.build_file_tree_from_m3u(m3u_directory)
    file_tree_matcher_old.save_to_json("file_tree_m3u.json")

    file_tree_matcher = FileTreeMatcher(root_dir, white_extension)
    file_tree_matcher.build_file_tree()
    file_tree_matcher.save_to_json("file_tree.json")

    match_map = file_tree_matcher.get_path_mapping(file_tree_matcher_old.file_tree)
    with open('map.json', 'w', encoding='utf-8') as f:
            print(f"匹配完毕，共匹配到{len(match_map)}项")
            f.write(json.dumps(match_map, ensure_ascii=False, indent=4))
    