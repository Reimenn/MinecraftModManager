from Utils import LoaderType
import dataclasses

from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from data.mod.ModFile import ModFile


@dataclasses.dataclass
class ModDepend(object):
    mod_id: str
    mandatory: bool
    version_range: str = ''
    ordering: str = ''
    side: str = ''


@dataclasses.dataclass
class ModInfo(object):
    """表示一个加载器中的 MOD 信息
    """
    file: "ModFile"
    name: str
    mod_id: str
    version: str
    dependencies: list[ModDepend]
    mc_version: str
    description: str
    links: dict[str, str]
    authors: list[str]
    icon: bytes | None

    child_mods: list["ModFile"]
    provide_mods_id: list[str]

    loader: LoaderType

    def include_mod_by_id(self, mod_id: str) -> bool:
        return self.get_include_mod_by_id(mod_id) is not None

    def get_include_mod_by_id(self, mod_id: str) -> Union["ModFile", None]:
        if self.mod_id == mod_id:
            return self.file
        for mod in self.child_mods:
            get = mod.get_include_mod_by_id(mod_id, self.loader)
            if get:
                return get
        return None
