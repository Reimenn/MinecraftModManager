import dataclasses
import json
import os
import os.path as path
import shutil
from typing import Callable, List

from data.mod.ModFile import ModFile


class GameType(object):
    fabric: str = 'fabric'
    quilt: str = 'quilt'
    forge: str = 'forge'
    vanilla: str = 'vanilla'
    other: str = 'other'


_DEFAULT_MC_VERSION = '未知 mc 版本'


@dataclasses.dataclass
class Game:
    dir_name: str
    """目录名称"""
    full_dir_path: str = ''
    """完整的目录"""
    game_type: str = GameType.other
    """游戏类型，值为 GameType 类中的字段"""
    version: str = _DEFAULT_MC_VERSION
    """游戏版本"""
    mod_list: list[ModFile] | None = None
    """mod 列表"""

    def get_mods_or_load(self, on_load_one: Callable[[ModFile], None] | None = None,
                         on_load_over: Callable[[list[ModFile]], None] | None = None) -> list[ModFile]:
        """获取 mod 们，若还没有读取则自动读取

        Args:
            on_load_one 成功读取一个 mod 时的回调.
            on_load_over 读取完毕时的回调.

        Returns:
            mod 们
        """
        if self.mod_list is None:
            self.reload_mods(on_load_one, on_load_over)

        assert self.mod_list
        return self.mod_list

    def reload_mods(self, on_load_one: Callable[[ModFile], None] | None = None,
                    on_load_over: Callable[[list[ModFile]], None] | None = None) -> None:
        """重新加载 mod

        Args:
            on_load_one 成功读取一个 mod 时的回调.
            on_load_over 读取完毕时的回调.
        """
        from data import load_mods
        self.mod_list = load_mods(os.path.join(self.full_dir_path, 'mods'),
                                  on_load_one=on_load_one, on_load_over=on_load_over)

    def has_mod_by_id(self, mod_id: str) -> bool:
        """根据 mod id 判断是否存在某个 mod

        Args:
            mod_id (str): mod id

        Returns:
            bool: 是否存在这个 mod 
        """

        if mod_id is None:
            return False
        for mod in self.get_mods_or_load():
            if mod.include_mod_by_id(mod_id):
                return True
        return False

    def get_mod_by_id(self, mod_id: str) -> ModFile | None:
        for mod in self.get_mods_or_load():
            if mod_id in mod.get_ids():
                return mod

    def has_mod_by_file(self, mod_file: str) -> bool:
        """根据 mod 文件名判断是否存在某个 mod, 注意这只能判断是否存在同文件名 mod，这仅仅检查文件名。

        Args:
            mod_file (str): 文件名，不带路径

        Returns:
            bool: 是否存在 mod
        """
        for mod in self.get_mods_or_load():
            basename = os.path.basename(mod.full_file_path)
            if basename.lower() == mod_file.lower():
                return True
        return False

    def add_mod(self, mod: ModFile) -> None:
        """添加一个 mod 到这个游戏，这会把 mod 文件复制进 mods 文件夹。
        若存在同名的 mod 则会自动添加数字前缀。
        Args:
            mod (ModInfo): 要被添加的 mod
        """
        if self.mod_list is None:
            self.reload_mods()
        basename = os.path.basename(mod.full_file_path)
        new_file_path: str = path.join(
            self.full_dir_path, 'mods', basename)
        mod = mod.copy_to(
            path.join(self.full_dir_path, 'mods', basename)
        )
        assert self.mod_list
        self.mod_list.append(mod)

    def remove_mod(self, mod: ModFile) -> None:
        """删除 mod 和对应文件。

        Args:
            mod (ModInfo): 要删除的 mod。
        """
        if mod not in self.get_mods_or_load():
            return
        os.remove(mod.full_file_path)
        if self.mod_list:
            self.mod_list.remove(mod)

    @staticmethod
    def create(version_dir: str) -> 'Game':
        """创建 GameInfo

        Args:
            version_dir (str): 游戏目录，这里面应该包含一个和目录同名的 json 文件。

        Returns:
            GameInfo: 游戏信息
        """
        dir_name = path.basename(version_dir)
        result = Game(dir_name)
        result.full_dir_path = os.path.abspath(version_dir)
        json_file_path = path.join(version_dir, dir_name + '.json')

        if not path.exists(json_file_path):
            return result

        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_root: dict = json.loads(f.read())
        main_class = json_root.get('mainClass', '')
        if main_class.startswith('cpw.mods.'):
            result.game_type = GameType.forge
        elif main_class.startswith('net.fabricmc.'):
            result.game_type = GameType.fabric
        elif main_class.startswith('net.minecraft.client.'):
            result.game_type = GameType.vanilla
        else:
            result.game_type = GameType.other
            return result

        result.version = json_root.get('clientVersion', _DEFAULT_MC_VERSION)
        if result.version == _DEFAULT_MC_VERSION:
            patches: List[dict] = json_root.get('patches', [])
            for p in patches:
                if p.get('id', '') == 'game':
                    result.version = p.get('version', _DEFAULT_MC_VERSION)
                    break

        return result
