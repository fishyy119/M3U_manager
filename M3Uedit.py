import os
import json
from LoadFileTree import SettingLoader

def update_m3u_file(m3u_directory: str,
                    input_file: str, 
                    output_file: str, 
                    mapping_file: str
                    ) -> None:
    # 从外部的 map.json 文件中读取 path_mapping
    with open(mapping_file, 'r', encoding='utf-8') as f:
        path_mapping = json.load(f)

    updated_paths = []
    input_file = os.path.join(m3u_directory, input_file)
    output_file = os.path.join(m3u_directory, output_file)
    # 读取旧的 m3u 文件并替换路径
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            # 处理每一行的路径
            old_path = line.strip()  # 移除行尾的换行符
            directory, file_name = os.path.split(old_path)  # 获取文件名
            # 如果在路径映射中找到了对应的新路径
            if directory in path_mapping:
                new_directory = path_mapping[directory]  # 获取新路径
                # 将新路径与文件名拼接，并添加到更新后的列表中
                updated_paths.append(os.path.join(new_directory, file_name))
            else:
                # 如果路径映射中没有对应的新路径，则保持原路径不变
                updated_paths.append(old_path)

    # 将更新后的路径写入同一个文件中
    with open(output_file, 'w', encoding='utf-8') as f:
        for updated_path in updated_paths:
            f.write(updated_path + '\n')

if __name__ == "__main__":
    setting_loader = SettingLoader('setting.json')
    settings = setting_loader.read_settings()
    m3u_directory = settings['m3u_directory']  # m3u存储路径
    m3u_directory = r'C:\Users\18309\Music\Dopamine\Playlists'
    mapping_file = 'map.json'  # 外部的 map.json 文件路径
    
    for m3uname in os.listdir(m3u_directory):
        if m3uname.endswith(".m3u"):
            update_m3u_file(m3u_directory, m3uname, m3uname, mapping_file)
