import json
from zipfile import ZipFile
from data.mod.ModFile import ModFile
from data.mod.ModInfo import ModDepend
from data.mod.parser.ModParserBase import ModParserBase
from data.mod import log
from io import BytesIO

_QUILT_MOD_INFO_FILE = 'quilt.mod.json'


class QuiltModParser(ModParserBase):
    @staticmethod
    def supported(jar: ZipFile) -> bool:
        if _QUILT_MOD_INFO_FILE in [i.filename for i in jar.filelist]:
            return True
        return False

    def _init_parse_json(self):
        self.loader_info: dict = self.json.get('quilt_loader', {})
        if not self.loader_info:
            log.error(
                f"没能在 {self.mod_file.get_full_path()} 里找到 quilt_loader 字段"
            )
            self.error = True
            return
        self.metadata: dict = self.loader_info.get('metadata', {})
        if not self.metadata:
            log.error(
                f"没能在 {self.mod_file.get_full_path()} 里找到 metadata 字段"
            )
            self.error = True

    def __init__(self, jar: ZipFile, mod_file: ModFile):
        super().__init__(jar, mod_file)
        self.loader = 'quilt'
        json_source = jar.read(_QUILT_MOD_INFO_FILE)
        try:
            self.json: dict = json.loads(json_source)
            self._init_parse_json()
        except json.decoder.JSONDecodeError as e:
            try:
                self.json: dict = json.loads(
                    json_source.replace(b'\n', b' ')
                )
                self._init_parse_json()
            except Exception as e:
                log.error(
                    f"用 quilt 解析来自 {self.mod_file.get_full_path()} 的 mod 失败，"
                    f"无法在初始化时读取 JSON 文件：{e}")
                self.error = True

    def get_authors(self) -> list[str]:
        if self.error:
            return []
        result: list[str] = []
        for author in self.metadata.get('contributors', {}):
            if author and isinstance(author, str):
                result.extend(author.split(','))
            elif isinstance(author, dict):
                for k, v in author.items():
                    result.append(k + ":" + v)
        return result

    def get_depends(self) -> list[ModDepend]:
        if self.error:
            return []
        result: list[ModDepend] = []

        for dep in self.loader_info.get('depends', []):
            if isinstance(dep, str):
                result.append(ModDepend(mod_id=dep, mandatory=True))
                continue
            mod_id = dep.get('id', '')
            if not mod_id:
                continue
            if mod_id in ['minecraft', 'fabricloader', 'java', 'fabric']:
                continue

            result.append(ModDepend(
                mod_id=mod_id,
                mandatory=True,
                version_range=dep.get('versions', '0.0.0')
            ))

        return result

    def get_mc_version(self) -> str:
        if self.error:
            return ""
        deps = self.json.get('depends', [])
        for dep in deps:
            mod_id: str = dep.get('id', '')
            if mod_id.lower() == 'minecraft':
                return dep.get('versions', '0.0.0')
        return '0.0.0'

    def get_description(self) -> str:
        if self.error:
            return ""

        return self.metadata.get('description', '')

    def get_links(self) -> dict[str, str]:
        if self.error:
            return {}
        result: dict[str, str] = {}
        for k, v in self.metadata.get('contact', {}).items():
            if isinstance(k, str) and isinstance(v, str):
                result[k] = v
        return result

    def get_icon(self) -> bytes | None:
        if self.error:
            return None
        icon = self.metadata.get('icon', None)
        if icon is None:
            return None
        try:
            with self.jar.open(icon, 'r') as f:
                return f.read()
        except Exception:
            log.info(f"打开 icon 图标失败，{self.mod_file.get_full_path()}")
            return None

    def get_mod_id(self) -> str:
        if self.error:
            return ''
        return self.loader_info.get('id', '')

    def get_name(self) -> str:
        if self.error:
            return ''
        return self.metadata.get('name', '')

    def get_provide_mods_id(self) -> list[str]:
        if self.error:
            return []
        # TODO 还不确定 quilt mod 的 provide 是不是在这个路径
        return self.loader_info.get('provides', [])

    def get_version(self) -> str:
        if self.error:
            return '0.0.0'
        return self.loader_info.get('version', '0.0.0')

    def get_child_mods(self) -> list[ModFile]:
        if self.error:
            return []

        jars: list[str] = [jar for jar in self.loader_info.get('jars', [])
                           if isinstance(jar, str)]

        if jars:
            log.info(
                f"准备为 {self.mod_file.get_full_path()} 解析 {len(jars)} 个子 mod")

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
                    f"在 {self.mod_file.get_full_path()} 中解析子 mod {jar} 时出现错误：{e}")
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


if __name__ == '__main__':
    from data.mod.ModFile import ModFile
    mods = ModFile.create(
        '/980/Minecraft/mods/all/voicechat-quilt-1.19.2-2.3.8.jar')
    if mods is None:
        print('>>>>')
    else:
        print(mods.get_names())
        print(mods.get_ids())
        print(mods.get_ids())
