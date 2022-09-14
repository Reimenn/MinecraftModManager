import os
import os.path as path
import shutil
import sys
from webbrowser import get
import zipfile
import toml
import json
import dataclasses

_FABRIC_MOD_INFO_FILE = 'fabric.mod.json'
_QUILT_MOD_INFO_FILE = 'quilt.mod.json'
_FORGE_MOD_INFO_FILE = 'META-INF/mods.toml'
_JAR_INFO_FILE = 'META-INF/MANIFEST.MF'

_DEFAULT_NAME = '无名 mod'
_DEFAULT_MOD_ID = '未知 id'
_DEFAULT_VERSION = '未知版本'
_DEFAULT_MC_VERSION = '不明 mc 版本'
_DEFAULT_LOADER = '不明加载器'
_DEFAULT_MOD_DESC = ''



def _mf(zip_file: zipfile.ZipFile, var: dict[str, str]) -> dict[str, str]:
    if var:
        return var

    result: dict[str, str] = {}
    for line in zip_file.read(_JAR_INFO_FILE).decode('utf-8').split('\n'):
        p = line.find(':')
        result[line[0:p].strip()] = line[p + 1:].strip()
    return result


@dataclasses.dataclass
class ModDepend(object):
    mod_id: str
    mandatory: bool
    version_range: str = ''
    ordering: str = ''
    side: str = ''


@dataclasses.dataclass
class Mod:
    file_name: str
    """MOD 文件名"""
    name: str = _DEFAULT_NAME
    mod_id: str = _DEFAULT_MOD_ID
    version: str = _DEFAULT_VERSION
    dependencis: list[ModDepend] = dataclasses.field(default_factory=list)
    mc_version: str = _DEFAULT_MC_VERSION
    loader: str = _DEFAULT_LOADER
    description: str = _DEFAULT_MOD_DESC
    homepage: str = ""
    authors: str = ""
    icon: bytes | None = None
    full_file_path: str = ''

    def __post__init__(self):
        self.dependencis = []

    def get_search_text(self) -> str:
        """ 获取这个mod的可搜索内容，包含名字、文件名、id、描述。
        """
        return self.name + self.file_name + self.mod_id

    def __from_fabric_jar(self, zip_file: zipfile.ZipFile) -> None:
        fabric_mod_json = zip_file.read(_FABRIC_MOD_INFO_FILE)
        try:
            json_root: dict = json.loads(fabric_mod_json)
        except json.decoder.JSONDecodeError as e:
            try:
                json_root: dict = json.loads(
                    fabric_mod_json.replace(b'\n', b' '))
            except Exception as e:
                sys.stderr.write(str(e))
                return

        # 图标
        
        self.icon = None
        icon_path = json_root.get('icon', None)
        try:
            if icon_path:
                f = zip_file.open(icon_path, 'r')
                self.icon = f.read()
                f.close()
        except Exception as e:
            pass

        # 作者
        temp = json_root.get('authors', [])
        authors = []
        for i in temp:
            if isinstance(i, dict):
                if name := i.get('name', ''):
                    authors.append(name)
            else:
                authors.append(i)
        # 依赖设置
        jars: list[dict] = json_root.get('jars', {})
        jar_files: list[str] = []
        for jar in jars:
            jar_files.append(jar.get('file', ''))
        jar_files_str: str = '\n\n\n'.join(jar_files)

        for k, v in json_root.get('depends', {}).items():
            if k in ['minecraft', 'fabricloader', 'java']:
                continue
            if k in jar_files_str:
                continue
            self.dependencis.append(ModDepend(
                mod_id=k,
                mandatory=True,
                version_range=v
            ))

        # 信息填充
        self.name = json_root.get('name', _DEFAULT_NAME)
        self.mod_id = json_root.get('id', '')
        self.version = json_root.get('version', '')
        self.mc_version = json_root.get('depends', {}).get(
            'minecraft', _DEFAULT_MC_VERSION)

        self.homepage = json_root.get(
            'contact', {"homepage": ""}).get('homepage', "")
        self.authors = ', '.join(authors)
        self.description = json_root.get('description', '')

        if "version" in self.version:
            self.version = _DEFAULT_VERSION

    def __from_quilt_jar(self, zip_file: zipfile.ZipFile) -> None:
        quilt_mod_json = zip_file.read(_QUILT_MOD_INFO_FILE)
        try:
            json_root: dict = json.loads(quilt_mod_json)
        except json.decoder.JSONDecodeError as e:
            try:
                json_root: dict = json.loads(
                    quilt_mod_json.replace(b'\n', b' '))
            except Exception as e:
                return

        quilt_loader_info = json_root.get('quilt_loader', {})
        if not quilt_loader_info:
            return

        # 基础信息
        self.mod_id = quilt_loader_info.get('id', _DEFAULT_MOD_ID)
        self.version = quilt_loader_info.get('version', _DEFAULT_VERSION)
        self.dependencis = [i.get('id') for i in quilt_loader_info.get('depends', [])
                            if i.get('id', '')
                            and not i.get('id', '').startswith('quilt')
                            and i.get('id', '') != 'minecraft' and i.get('id', '') != 'java']
        # mc 版本
        self.mc_version = _DEFAULT_MC_VERSION
        for dep in quilt_loader_info.get('depends', []):
            if dep.get('id', '') == 'minecraft':
                self.mc_version = dep.get('versions', _DEFAULT_MC_VERSION)
                break

        metadata = quilt_loader_info.get('metadata', {})
        if not metadata:
            return
        self.name = metadata.get('name', _DEFAULT_NAME)
        self.description = metadata.get('description', _DEFAULT_MOD_DESC)
        authors: list[str] = []
        authors.extend(metadata.get('contributors', {}).keys())
        authors.extend(metadata.get('authors', []))
        self.authors = ', '.join(authors)
        self.homepage = metadata.get('contact', {}).get('homepage', '')

        # 图标
        icon: bytes | None = None
        icon_path = metadata.get('icon', None)
        try:
            if icon_path:
                f = zip_file.open(icon_path, 'r')
                icon = f.read()
                f.close()
        except Exception as e:
            pass
        self.icon = icon

        # 检查 version 是否正确
        if "version" in self.version:
            self.version = _DEFAULT_VERSION

    def __from_forge_jar(self, zip_file: zipfile.ZipFile) -> None:
        try:
            toml_str = zip_file.read(_FORGE_MOD_INFO_FILE).decode('utf-8')
            toml_str = '\n'.join([i.strip() for i in toml_str.split('\n')])
        except Exception as e:
            return

        toml_root: dict = toml.loads(toml_str)
        toml_mods: dict = toml_root.get('mods', [{}])[0]
        if not toml_mods:
            return

        # 获取 图标
        icon: bytes | None = None
        icon_path = toml_mods.get('logoFile', None)
        try:
            if icon_path:
                f = zip_file.open(icon_path, 'r')
                icon = f.read()
                f.close()
        except Exception as e:
            pass
        # MOD 信息
        self.name = toml_mods.get('displayName', _DEFAULT_NAME)
        self.mod_id = toml_mods.get('modId', _DEFAULT_MOD_ID)
        self.version = toml_mods.get('version', _DEFAULT_VERSION)
        self.description = toml_mods.get('description', _DEFAULT_MOD_DESC)
        self.homepage = toml_mods.get('displayURL', "")
        self.authors = toml_mods.get('authors', "")
        self.icon = icon
        self.dependencis = [i for i in self.dependencis if i !=
                            'minecraft' and i != 'forge']

        # 获取 mc 版本和依赖信息
        dependencies: list[dict] = toml_root.get(
            'dependencies', {}).get(self.mod_id, [])
        self.mc_version: str = _DEFAULT_MC_VERSION
        self.dependencis = []
        for dep in dependencies:
            depend: ModDepend = ModDepend(
                mod_id=dep.get('modId', ''),
                mandatory=dep.get('mandatory', True),
                version_range=dep.get('versionRange', ''),
                ordering=dep.get('ordering', ''),
                side=dep.get('side', '')
            )
            if depend.mod_id == 'minecraft':
                self.mc_version = dep.get('versionRange', _DEFAULT_MC_VERSION)
                continue
            if depend.mod_id == 'forge':
                continue
            self.dependencis.append(depend)

        # 从 MANIFEST.MF 文件补充缺失信息
        mf = {}
        if not self.version or self.version == _DEFAULT_VERSION or 'version' in self.version.lower():
            self.version = _mf(zip_file, mf).get(
                'Implementation-Version', _DEFAULT_VERSION)
        if not self.name or self.name == _DEFAULT_NAME:
            self.name = _mf(zip_file, mf).get(
                'Implementation-Title', _DEFAULT_NAME)
        if not self.mod_id or self.mod_id == _DEFAULT_MOD_ID:
            self.mod_id = _mf(zip_file, mf).get(
                'Specification-Title', _DEFAULT_MOD_ID)

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

    def copy_to(self, target_dir: str) -> 'Mod':
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
        return Mod.create(new_path)

    def __str__(self) -> str:
        return f'{self.loader} | {self.name} | 来自文件 {self.file_name}'

    @staticmethod
    def create(file_path: str) -> 'Mod':
        """根据文件, 创建 ModInfo

        Args:
            file_path (str): .jar 文件路径
        """
        result = Mod(file_name=os.path.basename(file_path))
        result.full_file_path = os.path.abspath(file_path)
        zip_file = zipfile.ZipFile(file_path)
        result.loader = get_mod_loader(zip_file)
        match result.loader:
            case 'forge':
                result.__from_forge_jar(zip_file)
            case 'fabric':
                result.__from_fabric_jar(zip_file)
            case 'quilt':
                result.__from_quilt_jar(zip_file)
            case _:
                if 'fabric' in result.loader:
                    result.__from_fabric_jar(zip_file)
                if 'quilt' in result.loader:
                    result.__from_quilt_jar(zip_file)

        return result

    def __hash__(self) -> int:
        return hash(self.full_file_path)


def get_mod_loader(zip_file: zipfile.ZipFile) -> str:
    """根据 jar 文件内的描述判断 mod 的加载器

    Args:
        zip_file (ZipFile): jar 文件

    Returns:
        str: 加载器, 可能是 forge,fabric,quilt,other或包含多个加载器的组合形式(中间用 or 连接)
    """
    zip_in_file_list_map = {i.filename: i for i in zip_file.filelist}
    is_fabric = _FABRIC_MOD_INFO_FILE in zip_in_file_list_map
    is_forge = _FORGE_MOD_INFO_FILE in zip_in_file_list_map
    is_quilt = _QUILT_MOD_INFO_FILE in zip_in_file_list_map
    if is_quilt and is_fabric:
        return 'quilt or fabric'
    if is_quilt:
        return 'quilt'
    if is_fabric and is_forge and zip_file.filename:
        has_fabric = 'fabric' in zip_file.filename
        has_forge = 'forge' in zip_file.filename
        if has_fabric and has_forge:
            return 'fabric or forge'
        if has_fabric:
            return 'fabric'
        if has_forge:
            return 'forge'
    if is_fabric:
        return 'fabric'
    if is_forge:
        return 'forge'
    return 'other'
