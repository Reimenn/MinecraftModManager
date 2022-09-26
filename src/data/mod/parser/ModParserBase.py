from abc import abstractmethod
from ast import main
from data.mod import log
from zipfile import ZipFile
from Utils import LoaderType
from data.mod.ModInfo import ModInfo, ModDepend
from data.mod.ModFile import ModFile


class ModParserBase(object):
    """这是个 Mod 解析器基类，实现新的解析器需要重写 get_ 开头的的全部方法。
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
        log.info(f"开始解析 {self.loader} mod: {self.mod_file.get_full_path()}")
        try:
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
            self.parse_over(result)
        except Exception as e:
            log.error(
                f"按照 {self.loader} 方式解析 {self.mod_file.get_full_path()} 出现异常：{e}"
            )
            import traceback as tb
            err = tb.format_tb(e.__traceback__)
            error_output: list[str] = ['']
            for line in err:
                error_output.append(line)
            log.error('\n\t'.join(error_output))

            return None

        if self.error:
            return None
        log.info(f"解析完成 {self.loader} mod: {self.mod_file.get_full_path()}")
        return result

    def parse_over(self, mod: ModInfo) -> None:
        """构建 ModInfo 后调用的后处理方法，可以对 ModInfo 进行最后一步完善。
        """
        pass

    def raise_error(self, message: str) -> None:
        self.error = True
        log.warning(
            f"按照 {self.loader} 方式解析 {self.mod_file.get_full_path()} 失败：" + message)

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


if __name__ == '__main__':
    from data.mod.ModFile import ModFile
    modf = ModFile.create(
        "/980/Minecraft/mods/all/Yuushya-Beta-0.10.2-forge.jar")
