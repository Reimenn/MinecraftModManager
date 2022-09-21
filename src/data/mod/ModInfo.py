import os
import os.path as path
from os.path import basename
import shutil
from typing import Union
from data.Utils import LoaderType
import dataclasses

f = False
if f:
    from data.mod.ModFile import ModFile as newModFile

_DEFAULT_NAME = '无名 mod'
_DEFAULT_MOD_ID = '未知 id'
_DEFAULT_VERSION = '未知版本'
_DEFAULT_MC_VERSION = '不明 mc 版本'
_DEFAULT_LOADER = '不明加载器'
_DEFAULT_MOD_DESC = ''


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
    file: 'newModFile'
    name: str
    mod_id: str
    version: str
    dependencies: list[ModDepend]
    mc_version: str
    description: str
    links: dict[str, str]
    authors: list[str]
    icon: bytes | None

    child_mods: list['newModFile']
    provide_mods_id: list[str]

    loader: LoaderType


@dataclasses.dataclass
class ModFile:
    full_file_path: str
    loaders: set[str] = dataclasses.field(default_factory=set)
    infos: dict[str, ModInfo] = dataclasses.field(default_factory=dict)
    file_name: str = ''

    parent: Union['ModFile', None] = None
    child_mods: list['ModFile'] = dataclasses.field(default_factory=list)
    provide_mods_id: list[str] = dataclasses.field(default_factory=list)

    def __post__init__(self):
        self.file_path = basename(self.full_file_path)

    def get_search_text(self) -> str:
        """ 获取这个mod的可搜索内容，包含名字、文件名、id、描述。
        """
        return self.name + self.file_name + self.mod_id
        return self.file_name

    def included_mod_by_id(self, mod_id: str) -> bool:
        if self.mod_id == mod_id:
            return True
        if mod_id in self.provide_mods_id:
            return True
        for mod in self.child_mods:
            if mod.included_mod_by_id(mod_id):
                return True
        return False

    def is_enabled(self) -> bool:
        return self.file_name.lower().endswith('.jar')

    def disable(self) -> None:
        if not self.is_enabled():
            return
        self.rename_file(self.file_name + '.disabled')

    def enable(self) -> None:
        if self.is_enabled():
            return
        self.rename_file(self.file_name[:self.file_name.rfind('.')])

    def rename_file(self, new_name: str) -> None:
        """重命名 mod 文件名

        Args:
            new_name (str): 新的mod文件名，不带路径，包含后缀。
        """
        new_file_name = new_name
        new_full_path = path.join(self.full_file_path, '../', new_file_name)
        os.rename(self.full_file_path, new_full_path)
        self.file_name = new_file_name

        self.full_file_path = path.abspath(new_full_path)

    def delete_file(self) -> None:
        """删除 mod 文件
        """
        os.remove(self.full_file_path)

    def copy_to(self, target_dir: str) -> 'ModFile':
        """把这个 mod 复制到某个目录

        Args:
            target_dir (str): 目标目录

        Returns:
            ModInfo: 新文件对应的 ModInfo
        """
        new_path = os.path.join(target_dir, self.file_name)
        ind = 0
        while path.exists(new_path):
            ind += 1
            new_path = os.path.join(target_dir, f'({ind})' + self.file_name)
        shutil.copy(self.full_file_path, new_path)
        import data.ModLoader
        return data.ModLoader.load_form_file(new_path)

    def __str__(self) -> str:
        return f'{self.loader} | {self.name} | 来自文件 {self.file_name}'

    def __hash__(self) -> int:
        return hash(self.full_file_path)
