from typing import Callable
from data.mod.ModFile import ModFile
from data.GameInfo import Game


class ModCheckResult(object):
    def __init__(self,
                 mod: ModFile,
                 game: Game,
                 message: str,
                 ) -> None:
        self.mod: ModFile = mod
        self.game: Game = game
        self.message: str = message
        self.action: Callable[['ModCheckResult'], None] | None = None

    def Action(self):
        if self.action:
            self.action(self)

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return self.__str__()


_tResults = dict[ModFile, list[ModCheckResult]]


def check_game(game: Game) -> _tResults:
    result: _tResults = {}
    for mod in game.get_mods_or_load():
        if not mod.enabled:
            continue
        mod_check: list[ModCheckResult] = []
        mod_check.extend(check_one_mod_depend(game, mod))
        loader_check = check_one_mod_loader(game, mod)
        if loader_check:
            mod_check.append(loader_check)
        if mod_check:
            result[mod] = mod_check
    return result


def check_one_mod_loader(game: Game, mod: ModFile) -> ModCheckResult | None:
    if game.game_type in mod.support_loaders():
        return None
    return ModCheckResult(
        mod, game, f"确定这是一个支持 {game.game_type} 的mod吗？"
    )


def check_one_mod_depend(game: Game, mod: ModFile) -> list[ModCheckResult]:
    info = mod.get_info(game.game_type)  # type: ignore
    if info is None:
        return []

    result: list[ModCheckResult] = []
    for dep in info.dependencies:
        if not dep.mandatory:
            continue
        if not game.has_mod_by_id(dep.mod_id):
            result.append(ModCheckResult(mod, game, f"缺少前置mod: {dep.mod_id}"))
            continue

        dep_mod = game.get_mod_by_id(dep.mod_id)
        if dep_mod is None:
            continue
        if not dep_mod.enabled:
            result.append(ModCheckResult(
                mod, game, f"前置mod: {dep.mod_id} 没有开启"))
            continue
    return result


if __name__ == '__main__':
    game: Game = Game.create(
        r'/980/Minecraft/.minecraft/versions/1.18.2-Fabric 0.14.9')
    result = check_game(game)
    for k, v in result.items():
        print(k, v)
