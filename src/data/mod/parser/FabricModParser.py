import json
from zipfile import ZipFile
from data.mod.ModFile import ModFile
from data.mod.ModInfo import ModDepend
from data.mod.parser.ModParserBase import ModParserBase
from data.mod import log
from io import BytesIO

_FABRIC_MOD_INFO_FILE = 'fabric.mod.json'


class FabricModParser(ModParserBase):
    @staticmethod
    def supported(jar: ZipFile) -> bool:
        if _FABRIC_MOD_INFO_FILE in [i.filename for i in jar.filelist]:
            return True
        return False

    def __init__(self, jar: ZipFile, mod_file: ModFile):
        super().__init__(jar, mod_file)
        self.loader = 'fabric'
        json_source = jar.read(_FABRIC_MOD_INFO_FILE)
        try:
            self.json: dict = json.loads(json_source)
        except json.decoder.JSONDecodeError as e:
            try:
                self.json: dict = json.loads(
                    json_source.replace(b'\n', b' ')
                )
            except Exception as e:
                self.raise_error(
                    "无法在初始化时解析 JSON，因为 {e}"
                )

    def get_authors(self) -> list[str]:
        if self.error:
            return []
        result: list[str] = []
        for author in self.json.get('authors', []):
            if isinstance(author, str) and author:
                result.append(author)
            elif isinstance(author, dict):
                if name := author.get('name', ''):
                    result.append(name)

        return result

    def get_depends(self) -> list[ModDepend]:
        if self.error:
            return []
        result: list[ModDepend] = []

        for k, v in self.json.get('depends', {}).items():
            if k in ['minecraft', 'fabricloader', 'java', 'fabric']:
                continue
            result.append(ModDepend(
                mod_id=k,
                mandatory=True,
                version_range=v
            ))

        return result

    def get_mc_version(self) -> str:
        if self.error:
            return ""
        return self.json.get('depends', {}).get('minecraft', '0.0.0')

    def get_description(self) -> str:
        if self.error:
            return ""

        return self.json.get('description', '')

    def get_links(self) -> dict[str, str]:
        if self.error:
            return {}
        result: dict[str, str] = {}
        for k, v in self.json.get('contact', {}).items():
            if isinstance(k, str) and isinstance(v, str):
                result[k] = v
        return result

    def get_icon(self) -> bytes | None:
        if self.error:
            return None
        icon = self.json.get('icon', None)
        if icon is None:
            return None
        try:
            with self.jar.open(icon, 'r') as f:
                return f.read()
        except Exception:
            log.info(f"打开 icon 图标失败，{self.mod_file.full_file_path}")
            return None

    def get_mod_id(self) -> str:
        if self.error:
            return ''
        return self.json.get('id', '')

    def get_name(self) -> str:
        if self.error:
            return ''
        return self.json.get('name', '')

    def get_provide_mods_id(self) -> list[str]:
        if self.error:
            return []
        return self.json.get('provides', [])

    def get_version(self) -> str:
        if self.error:
            return '0.0.0'
        return self.json.get('version', '0.0.0')

    def get_child_mods(self) -> list[ModFile]:
        if self.error:
            return []

        jars: list[str] = [jar.get('file', '')
                           for jar in self.json.get('jars', [])]
        if jars:
            log.info(
                f"准备为 {self.mod_file.full_file_path} 解析 {len(jars)} 个子 mod")

        result: list[ModFile] = []
        for jar in jars:
            log.info(f"解析子 mod {jar}")
            if not jar:
                continue

            try:
                f = self.jar.open(jar, 'r')
                jar_bytes = f.read()
                f.close()
            except Exception as e:
                log.warning(
                    f"在 {self.mod_file.full_file_path} 中解析子 mod {jar} 时出现错误：{e}")
                continue

            mod = ModFile.create_by_bytes(
                jar_bytes=BytesIO(jar_bytes),
                full_file_path=jar,
            )
            if mod is None:
                continue
            mod.parent = self.mod_file
            result.append(mod)

        return result
