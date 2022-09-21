from dataclasses import dataclass
from typing import IO, Union
from zipfile import ZipFile
from data.mod.ModInfo import ModInfo
from data.mod import log
import os


class LoadModError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__("加载 mod 文件错误：" + message)


_tModFile_None = Union[None, 'ModFile']


@dataclass
class ModFile(object):
    full_file_path: str
    mod_info: list[ModInfo]
    parent: _tModFile_None = None

    @staticmethod
    def create_by_bytes(jar_bytes: IO[bytes], full_file_path: str) -> _tModFile_None:

        result = ModFile(
            full_file_path=full_file_path,
            mod_info=[]
        )
        jar_zip: ZipFile = ZipFile(jar_bytes)

        from data.mod.parser import PARSERS
        for parser in PARSERS:
            if parser.supported(jar_zip):
                try:
                    info = parser(jar_zip, result).parse()
                    if info:
                        result.mod_info.append(info)
                except Exception as e:
                    log.error(
                        f"使用 {type(parser)} 解析 mod {full_file_path} 出现错误：{e}")

        if not result.mod_info:
            log.warning(
                f"没有从 {result.full_file_path} 中读取到任何一条有用的mod信息，因此忽略这个文件。")
            return None
        return result

    @staticmethod
    def create(jar_path: str) -> _tModFile_None:
        if not os.path.isfile(jar_path):
            log.warn("不能创建 ModField，因为 {jar_path} 不是文件。")
            return None
        with open(jar_path, 'rb') as f:
            mod = ModFile.create_by_bytes(f, os.path.abspath(jar_path))
        return mod


if __name__ == '__main__':
    mod = ModFile.create(
        "/run/media/rika/980/Minecraft/mods/s/iris-mc1.19.1-1.2.6.jar")
    if mod:
        for info in mod.mod_info:
            print(info.loader, info.name, info.mod_id, info.version)
            print(len(info.child_mods))
