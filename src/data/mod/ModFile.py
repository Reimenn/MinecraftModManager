from cmath import exp
from dataclasses import dataclass
from typing import IO, Union
from unittest import result
from zipfile import ZipFile
from Utils import LoaderType, clear_file_path_suffix
from data.mod.ModInfo import ModInfo
from data.mod import log
import os


_tModFile_None = Union[None, 'ModFile']


@dataclass
class ModFile(object):
    full_file_path: str
    mod_info: list[ModInfo]
    parent: _tModFile_None = None

    @staticmethod
    def create_by_bytes(jar_bytes: IO[bytes], full_file_path: str) -> 'ModFile':
        """从内存创建

        Args:
            full_file_path (str): 该 mod 文件的完整路径
        """

        result = ModFile(
            full_file_path=full_file_path,
            mod_info=[]
        )
        jar_zip: ZipFile = ZipFile(jar_bytes)

        from data.mod.parser import PARSERS
        for parser in PARSERS:
            if not parser.supported(jar_zip):
                continue
            try:
                info = parser(jar_zip, result).parse()
                if info:
                    result.mod_info.append(info)
            except Exception as e:
                log.error(
                    f"使用 {parser} 解析 mod {full_file_path} 出现错误：")

        if not result.mod_info:
            log.warning(
                f"没有从 {result.full_file_path} 中读取到任何一条有用的mod信息，因此忽略这个文件。")
        return result

    @staticmethod
    def create(jar_path: str) -> _tModFile_None:
        """从文件创建
        """
        if not os.path.isfile(jar_path):
            log.warn("不能创建 ModField，因为 {jar_path} 不是文件。")
            return None
        with open(jar_path, 'rb') as f:
            mod = ModFile.create_by_bytes(f, os.path.abspath(jar_path))
        return mod

    def support_loaders(self) -> list[LoaderType]:
        """获取支持的 mod 加载器
        """
        return [i.loader for i in self.mod_info]

    def get_info(self, loader: LoaderType) -> ModInfo | None:
        """获取某个 mod info
        """
        for info in self.mod_info:
            if info.loader == loader:
                return info
        return None

    def include_mod_by_id(self, mod_id: str, only_loader: LoaderType | None = None) -> bool:
        """是否包含某个mod

        Args:
            mod_id (str): mod 的 id
            only_loader (LoaderType | None, optional): 仅限某个 mod 加载器，默认为 None 表示任意加载器。
        """
        return self.get_include_mod_by_id(mod_id, only_loader) is not None

    def get_include_mod_by_id(self, mod_id: str, only_loader: LoaderType | None = None) -> Union['ModFile', None]:
        """获取某个子mod

        Args:
            mod_id (str): mod 的 id
            only_loader (LoaderType | None, optional): 仅限某个 mod 加载器，默认为 None 表示任意加载器。
        """
        if only_loader:
            info = self.get_info(only_loader)
            if info:
                return info.get_include_mod_by_id(mod_id)
        else:
            for info in self.mod_info:
                child_mod = info.get_include_mod_by_id(mod_id)
                if child_mod:
                    return child_mod
        return None

    def in_search(self, key: str, only_loader: LoaderType | None = None) -> bool:
        """传入一个关键字，返回该关键字能否搜索到这个 mod 文件。
        搜索内容包含名字、描述、mod id，并且忽略大小写

        Args:
            key (str): 搜索关键字
            only_loader (LoaderType | None, optional): 仅限某个 mod 加载器，默认为 None 表示任意加载器。
        """
        target: list[ModInfo] = []
        if only_loader:
            if info := self.get_info(only_loader):
                target.append(info)
        else:
            target = self.mod_info

        key = key.lower()
        content: list[str] = []
        for info in target:
            content.append(info.name)
            content.append(info.mod_id)
            content.append(info.description)
        content_str = ','.join(content).lower()

        return key in content_str

    @property
    def enabled(self) -> bool:
        return self.full_file_path.endswith('.jar')

    @enabled.setter
    def enabled(self, value: bool):
        if value == self.enabled:
            return
        new_path: str = clear_file_path_suffix(self.full_file_path, [
            'jar', 'disable', 'disabled'])
        if value:
            new_path += '.jar'
        else:
            new_path += '.jar.disabled'
        self.move_to(new_path)

    def move_to(self, target_path: str):
        """移动这个mod文件
        """
        os.rename(self.full_file_path, target_path)
        self.full_file_path = target_path

    def copy_to(self, target_path: str) -> 'ModFile':
        """复制 mod 文件到一个新的地方，并返回新的 ModFile
        """
        if self.parent:
            raise Exception(f"不能复制子 mod {self.get_full_path()}")
        import shutil
        shutil.copy(self.full_file_path, target_path)
        new_mod = ModFile.create(target_path)
        if new_mod is None:
            raise Exception(
                f"复制 mod {self.get_full_path()} 到 {target_path} 失败。")
        return new_mod

    def get_full_path(self) -> str:
        """获取完整的路径，如果是子mod，则在多个mod中用英文冒号: 分割
        """
        if self.parent:
            return self.parent.get_full_path() + ":" + self.full_file_path
        return self.full_file_path

    def delete_file(self):
        """删除 mod 文件
        """
        os.remove(self.full_file_path)

    def __hash__(self) -> int:
        return hash(self.get_full_path)

    def get_names(self) -> list[str]:
        """获取不重复 mod 名称列表
        """
        result = []
        for info in self.mod_info:
            if info.name not in result:
                result.append(info.name)
        return result

    def get_ids(self) -> list[str]:
        """获取当前 mod 的不重复 id 列表
        """
        result = []
        for info in self.mod_info:
            if info.mod_id not in result:
                result.append(info.mod_id)
        return result

    def get_icon(self) -> bytes | None:
        for info in self.mod_info:
            if info.icon:
                return info.icon
        return None


if __name__ == '__main__':
    mod = ModFile.create(
        "/980/Minecraft/mods/s/iris-mc1.19.1-1.2.6.jar")
    if mod:
        for info in mod.mod_info:
            print(info.loader, info.name, info.mod_id, info.version)
            print(len(info.child_mods))
