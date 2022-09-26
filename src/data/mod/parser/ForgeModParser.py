import toml
from zipfile import ZipFile
from data.mod.ModFile import ModFile
from data.mod.ModInfo import ModDepend, ModInfo
from data.mod.parser.ModParserBase import ModParserBase
from data.mod import log


_FORGE_MOD_INFO_FILE = 'META-INF/mods.toml'
_JAR_INFO_FILE = 'META-INF/MANIFEST.MF'


class ForgeModParser(ModParserBase):
    @staticmethod
    def supported(jar: ZipFile) -> bool:
        file_list = [file.filename for file in jar.filelist]
        return _FORGE_MOD_INFO_FILE in file_list

    def __init__(self, jar: ZipFile, mod_file: ModFile) -> None:
        super().__init__(jar, mod_file)
        self.loader = "forge"
        try:
            toml_str = jar.read(_FORGE_MOD_INFO_FILE).decode('utf-8')
            toml_str = '\n'.join(line.strip()
                                 for line in toml_str.splitlines())
        except Exception as e:
            self.raise_error(
                f"读取 {_FORGE_MOD_INFO_FILE} 失败，因为 {e}"
            )
            return
        self.toml: dict = toml.loads(toml_str)
        self.toml_mods: dict = self.toml.get('mods', [{}])[0]
        if not self.toml_mods:
            self.raise_error(
                f"没能从 {_FORGE_MOD_INFO_FILE} 中读取到 mods 信息。"
            )
            return
        self.deps: list[ModDepend] | None = None

    def parse_over(self, mod: ModInfo) -> None:
        no_version = 'version' in mod.version.lower() or mod.version == '0.0.0'
        no_name = bool(mod.name)
        no_id = bool(mod.mod_id)
        if no_version or no_name or no_id:
            info: dict[str, str] = {}
            info_str = self.jar.read(_JAR_INFO_FILE).decode('utf-8')
            for line in info_str.splitlines():
                p = line.find(':')
                info[line[0:p].strip()] = line[p + 1:].strip()
            if no_version:
                mod.version = info.get('Implementation-Version', '0.0.0')
            if no_name:
                mod.name = info.get('Implementation-Title', '')
            if no_id:
                mod.mod_id = info.get('Specification-Title', '')

    def get_icon(self) -> bytes | None:
        logo = self.toml_mods.get('logoFile', None)
        if logo is None:
            return None
        if not isinstance(logo, str):
            return None

        try:
            with self.jar.open(logo, 'r') as f:
                return f.read()
        except Exception as e:
            log.warning(
                f"{self.mod_file.full_file_path} 明明有 logoFile 设定但读取文件失败。")
            return None

    def get_name(self) -> str:
        return self.toml_mods.get('displayName', '')

    def get_mod_id(self) -> str:
        return self.toml_mods.get('modId', '')

    def get_version(self) -> str:
        return self.toml_mods.get('version', '0.0.0')

    def get_description(self) -> str:
        return self.toml_mods.get('description', '')

    def get_links(self) -> dict[str, str]:
        homepage = self.toml_mods.get('displayUrl', '')
        if not homepage:
            return {}
        return {"homepage": homepage}

    def get_authors(self) -> list[str]:
        authors = self.toml_mods.get('authors', '')
        if isinstance(authors, list):
            return [str(i) for i in authors]
        if isinstance(authors, str):
            return [i.strip() for i in authors.split(',')]
        return []

    def _get_depend_list(self) -> list[ModDepend]:
        if self.deps is not None:
            return self.deps

        mod_id = self.get_mod_id()
        depend_list: list[dict]\
            = self.toml.get('dependencies', {}).get(mod_id, [])
        result = []
        for dep in depend_list:
            result.append(ModDepend(
                mod_id=dep.get('modId', ''),
                mandatory=str(dep.get('mandatory', False)).lower() == 'true',
                version_range=dep.get('versionRange', ''),
                ordering=dep.get('ordering', ''),
                side=dep.get('side', '')
            ))
        return result

    def get_mc_version(self) -> str:
        for dep in self._get_depend_list():
            if dep.mod_id == 'minecraft':
                return dep.version_range
        return '0.0.0'

    def get_depends(self) -> list[ModDepend]:
        result = []
        for dep in self._get_depend_list():
            if dep.mod_id in ['forge', 'java', 'minecraft']:
                continue
            result.append(dep)
        return result

    def get_provide_mods_id(self) -> list[str]:
        return []

    def get_child_mods(self) -> list[ModFile]:
        return []
