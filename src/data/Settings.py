import os
import dataclasses
from typing import List, Dict


@dataclasses.dataclass
class Settings:
    _settings_file_path: str
    """设置文件存放的目录"""
    game_version_dir: str = "./.minecraft/versions"
    local_mods_dir: str = "./local_mods"
    global_size: float = 1
    
    def save(self):
        """保存设置"""
        with open(self._settings_file_path, 'w', encoding='utf-8') as f:
            for field in SettingsFields:
                if str(field.name).startswith('_'):
                    continue
                value = str(self.__getattribute__(field.name))
                f.write(field.name + "=" + value + "\n")
        
    @staticmethod
    def create(settings_file_path: str = "./settings.cfg") -> 'Settings':
        """从文件中读取设置"""
        if not os.path.exists(settings_file_path):
            new_s = Settings(settings_file_path)
            new_s.save()
            return new_s
        with open(settings_file_path, 'r', encoding='utf-8') as f:
            res = Settings(settings_file_path)
            for line in f.read().splitlines():
                if len(line) == 0:
                    continue
                key = line[0:line.find('=')]
                value = line[line.find('=') + 1:]
                if SettingsFieldsTypeMap[key] == int:
                    value = int(value)
                elif SettingsFieldsTypeMap[key] == float:
                    value = float(value)
                res.__setattr__(key, value)
            return res

    def get_size(self, number: int) -> int:
        return int(number * self.global_size)


SettingsFields: List[dataclasses.Field] = dataclasses.fields(
    Settings)  # type: ignore
SettingsFieldsTypeMap: Dict[str, type] = {
    i.name: i.type for i in SettingsFields}

_SETTINGS: 'Settings' = None  # type: ignore


def get_settings() -> 'Settings':
    global _SETTINGS
    if _SETTINGS is None:
        _SETTINGS = Settings.create()
    return _SETTINGS


settings = get_settings()
'''全局唯一的 settings 实例'''
