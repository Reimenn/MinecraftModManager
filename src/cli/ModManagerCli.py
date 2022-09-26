from cli.CommandClass import CommandBase
from data import ModManager, settings, Game


class ModManagerCli(CommandBase):
    def __init__(self) -> None:
        super().__init__()
        self.mm: ModManager = ModManager()

    def cmd_games(self, *args: str):
        game_list = self.mm.get_games_or_load()
        yield f"获取到 {len(game_list)} 个游戏："
        yield f"依次展示 加载器、mc版本、文件夹"
        for game in game_list:
            yield f"{game.game_type}\t{game.version}\t{game.dir_name}"
        yield ""

    def cmd_mods(self, *args: str):
        mod_list = self.mm.get_mods_or_load()
        yield f"获取到 {len(mod_list)} 个本地 mod"
        yield f"依次展示 mod名、加载器、mod id"
        if 'null' in args:
            for mod in mod_list:
                if not mod.mod_info:
                    yield f"{'|'.join(mod.get_names())}\t{','.join(mod.support_loaders())}\t{mod.get_ids()}\t{mod.get_full_path()}"
        else:
            for mod in mod_list:
                yield f"{'|'.join(mod.get_names())}\t{','.join(mod.support_loaders())}\t{mod.get_ids()}\t{mod.get_full_path()}"
        yield ""
