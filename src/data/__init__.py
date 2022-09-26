from os import listdir
from os.path import isdir, join

from data.Settings import settings
from data.GameInfo import Game
from data.mod.ModFile import ModFile

from typing import Callable

ModInfoArray = list[ModFile]


def load_mods(root_dir: str,
              on_load_one: Callable[[ModFile], None] | None = None,
              on_load_over: Callable[[list[ModFile]], None] | None = None,
              ) -> ModInfoArray:
    """加载一个目录下的全部 jar 格式的 mod 文件并返回，包含两个加载中的回调。

    Args:
        root_dir: mod 目录.
        on_load_one: 读取一个 mod 的回调.
        on_load_over: 读取结束后的回调.

    Returns:
        list[ModInfo]: ModInfo 列表
    """
    result: ModInfoArray = []
    if not isdir(root_dir):
        if on_load_over:
            on_load_over(result.copy())
        return result

    mods_file_list = listdir(root_dir)

    for mod_file_path in mods_file_list:
        # 仅读取 .jar 或 .jar.disabled 后缀的文件
        lf: str = mod_file_path.lower()
        if not (lf.endswith('.jar') or lf.endswith('.jar.disabled')):
            continue

        try:
            mod = ModFile.create(join(root_dir, mod_file_path))
        except Exception:
            continue
        if on_load_one and mod:
            on_load_one(mod)
        if mod:
            result.append(mod)

    if on_load_over:
        on_load_over(result.copy())
    return result


def load_games(root_dir: str,
               on_load_one: Callable[[Game], None] | None = None,
               on_load_over: Callable[[list[Game]], None] | None = None,
               ) -> list[Game]:
    """ 读取一个目录下的游戏版本们，支持两个回调

    Args:
        root_dir: 游戏目录根目录.
        on_load_one: 读取一个游戏的回调.
        on_load_over: 读取完成时的回调.

    Returns:
        list[GameInfo]: 游戏们
    """
    result: list[Game] = []
    if not isdir(root_dir):
        if on_load_over:
            on_load_over(result.copy())
        return result
    versions_dir_list = listdir(root_dir)
    for version_dir in versions_dir_list:
        try:
            game = Game.create(join(root_dir, version_dir))
            if on_load_one:
                on_load_one(game)
            result.append(game)
        except Exception:
            pass
    if on_load_over:
        on_load_over(result.copy())
    return result


class ModManager:
    __mm: 'ModManager' = None  # type: ignore

    def __init__(self):
        self.local_mods: list[ModFile] = []
        """仓库中的mod们"""
        self.games: list[Game] = []
        """游戏目录下的游戏们"""

    @staticmethod
    def get():
        if not ModManager.__mm:
            ModManager.__mm = ModManager()
        return ModManager.__mm

    def get_mods_or_load(self) -> list[ModFile]:
        """获取仓库中的mod，若没加载则自动加载。
        """
        if not self.local_mods:
            self.reload_local_mods()
        return self.local_mods

    def get_games_or_load(self) -> list[Game]:
        """获取游戏列表，若没加载则自动加载
        """
        if not self.games:
            self.reload_games()
        return self.games

    def reload_local_mods(self,
                          on_load_one: Callable[[ModFile], None] | None = None,
                          on_load_over: Callable[[
                              list[ModFile]], None] | None = None
                          ) -> None:
        """ 重新加载本地 mod 们
        """

        self.local_mods.clear()
        self.local_mods = load_mods(settings.local_mods_dir,
                                    on_load_one=on_load_one,
                                    on_load_over=on_load_over)

    def reload_games(self,
                     on_load_one: Callable[[Game], None] | None = None,
                     on_load_over: Callable[[
                         list[Game]], None] | None = None,
                     ) -> None:
        """重新加载本地的游戏们
        """
        self.games.clear()
        self.games = load_games(settings.game_version_dir,
                                on_load_one=on_load_one,
                                on_load_over=on_load_over)

    def add_mod(self, mod: ModFile) -> ModFile:
        """
        添加一个mod文件到本地mod文件存放目录，并返回新的mod
        Args:
            mod (ModInfo): 要添加的mod
        Returns:
            list[ModInfo]: 添加完成的mod
        """
        if mod in self.local_mods:
            return mod
        new_mod = mod.copy_to(settings.local_mods_dir)
        new_mod.enabled = True
        self.local_mods.append(new_mod)
        return new_mod


if __name__ == '__main__':
    mm = ModManager()
    mm.reload_local_mods()
    mm.reload_games()


__all__ = [
    'load_mods',
    'load_games',
    'Game',
    'ModFile',
    'ModManager'
]
