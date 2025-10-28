import json
from typing import List, Literal, Tuple, TypedDict, cast


class SettingsDict(TypedDict):
    root_dir: str
    m3u_directory: str
    white_extension: List[str]
    black_list_state: bool
    black_song: List[str]


LoaderResponse = Tuple[Literal[True], SettingsDict] | Tuple[Literal[False], str]


class SettingLoader:
    DEFAULT_SETTINGS = {
        "root_dir": "/path/to/songs/root/directory",
        "m3u_directory": "/path/to/m3u/files",
        "white_extension": [".mp3", ".wav", ".flac"],
        "black_list_state": False,
        "black_song": ["sample.mp3"],
    }

    def __init__(self, filename: str, gui: bool = False) -> None:
        """

        Args:
            filename (str): _description_
            gui (bool, optional): gui模式下，需要返回错误信息。否则控制台报错后直接退出。
        """
        print(f"{__file__} init")
        self.filename = filename
        self.gui_flag = gui

    def read_settings(self) -> LoaderResponse:
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                settings = cast(SettingsDict, json.load(f))
            return True, settings
        except FileNotFoundError:
            settings = self.DEFAULT_SETTINGS
            self.save_settings(cast(SettingsDict, settings))  # TODO: 验证
            msg = f"未发现设置文件'{self.filename}'，已自动创建，请前往设置"
            if not self.gui_flag:
                print(msg)
                exit(0)
            else:
                return False, msg

    def save_settings(self, settings: SettingsDict) -> None:
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
