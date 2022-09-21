from abc import abstractmethod
from dataclasses import dataclass
from json import load
from zipfile import ZipFile
from data.Utils import LoaderType
from data.mod.ModInfo import ModInfo, ModDepend
from data.mod.ModFile import ModFile


class ParseModError(Exception):
    def __init__(self) -> None:
        super().__init__("使用了不支持的 mod 解析器，建议解析前调用 supported 方法检查。")


class ModParserBase(object):
    """这是个 Mod 解析器基类，实现新的解析器需要重写除了 parse 以外的全部方法。
    在解析前可以到 init 方法中添加解析中要用到的字段，并在 clear 方法中删除他们。
    """

    def __init__(self, jar: ZipFile, mod_file: ModFile) -> None:
        self.jar: ZipFile = jar
        self.mod_file: ModFile = mod_file
        self.loader: LoaderType | None = None
        self.error: bool = False

    def parse(self) -> ModInfo | None:
        """ 从 jar 文件提取 mod 信息
        """
        if self.error:
            return None
        if self.loader is None:
            raise Exception("Mod 解析器没有设置 loader 属性！！！")
        result = ModInfo(
            loader=self.loader,
            file=self.mod_file,
            authors=self.get_authors(),
            child_mods=self.get_child_mods(),
            dependencies=self.get_depends(),
            description=self.get_description(),
            icon=self.get_icon(),
            mc_version=self.get_mc_version(),
            mod_id=self.get_mod_id(),
            name=self.get_name(),
            version=self.get_version(),
            provide_mods_id=self.get_provide_mods_id(),
            links=self.get_links()
        )
        if self.error:
            return None
        return result

    @staticmethod
    @abstractmethod
    def supported(jar: ZipFile) -> bool:
        """判断 jar 文件是否支持当前解析器解析
        """
        pass

    @abstractmethod
    def get_mod_id(self) -> str:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

    @abstractmethod
    def get_version(self) -> str:
        pass

    @abstractmethod
    def get_mc_version(self) -> str:
        pass

    @abstractmethod
    def get_icon(self) -> bytes | None:
        pass

    @abstractmethod
    def get_depends(self) -> list[ModDepend]:
        pass

    @abstractmethod
    def get_authors(self) -> list[str]:
        pass

    @abstractmethod
    def get_links(self) -> dict[str, str]:
        pass

    @abstractmethod
    def get_child_mods(self) -> list[ModFile]:
        pass

    @abstractmethod
    def get_provide_mods_id(self) -> list[str]:
        pass
