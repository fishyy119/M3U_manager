import json

class SettingLoader:
    DEFAULT_SETTINGS = {
        'root_dir': '/path/to/songs/root/directory',
        'm3u_directory': '/path/to/m3u/files',
        'white_extension': ['.mp3', '.wav', '.flac'],
        'black_list_state': False,
        'black_song': ['sample.mp3']
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
            print(f"未发现设置文件'{self.filename}'，已自动创建，请前往设置")
            settings = self.DEFAULT_SETTINGS
            self.save_settings(settings)
            exit(0)
        return settings

    def save_settings(self, 
                      settings: dict
                      ) -> None:
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)