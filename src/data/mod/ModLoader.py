from io import BytesIO
from zipfile import ZipFile, ZipInfo
import sys
import json
import toml
from data.mod.ModInfo import ModFile, ModDepend, ModInfo
from os.path import abspath, join, basename, exists, isfile, isdir

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


class ModLoadError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


def _mf(zip_file: ZipFile, var: dict[str, str]) -> dict[str, str]:
    if var:
        return var

    result: dict[str, str] = {}
    for line in zip_file.read(_JAR_INFO_FILE).decode('utf-8').split('\n'):
        p = line.find(':')
        result[line[0:p].strip()] = line[p + 1:].strip()
    return result


def zip_to_mod_info_if_fabric(mod: ModInfo, zip_file: ZipFile) -> None:
    fabric_mod_json = zip_file.read(_FABRIC_MOD_INFO_FILE)
    json_root: dict
    try:
        json_root = json.loads(fabric_mod_json)
    except json.decoder.JSONDecodeError as e:
        try:
            json_root = json.loads(
                fabric_mod_json.replace(b'\n', b' '))
        except Exception as e:
            sys.stderr.write(str(e))
            return

    # 图标
    mod.icon = None
    icon_path = json_root.get('icon', None)
    try:
        if icon_path:
            f = zip_file.open(icon_path, 'r')
            mod.icon = f.read()
            f.close()
    except Exception as e:
        pass

    # 信息填充
    mod.name = json_root.get('name', _DEFAULT_NAME)
    mod.mod_id = json_root.get('id', '')
    mod.version = json_root.get('version', '')

    # 作者
    temp = json_root.get('authors', [])
    authors = []
    for i in temp:
        if isinstance(i, dict):
            if name := i.get('name', ''):
                authors.append(name)
        else:
            authors.append(i)
    # 内部 jar 文件
    jars: list[str] = [jar.get('file', '')
                       for jar in json_root.get('jars', [])]
    for jar_file in jars:
        if not jar_file:
            continue
        inner_mod = ModInfo(mod.file)
        inner_mod.loader = 'fabric'
        inner_mod.parent = mod
        inner_zip = ZipFile(
            BytesIO(zip_file.open(jar_file).read()))
        inner_mod.__from_fabric_jar(inner_zip)
        mod.child_mods.append(inner_mod)

    # provides
    provides: list[str] = json_root.get('provides', [])
    for provide in provides:
        mod.provide_mods_id.append(str(provide))

    # 依赖设置
    for k, v in json_root.get('depends', {}).items():
        if k in ['minecraft', 'fabricloader', 'java', 'fabric']:
            continue
        if mod.included_mod_by_id(k):
            continue
        mod.dependencis.append(ModDepend(
            mod_id=k,
            mandatory=True,
            version_range=v
        ))

    mod.mc_version = json_root.get('depends', {}).get(
        'minecraft', _DEFAULT_MC_VERSION)

    mod.homepage = json_root.get(
        'contact', {"homepage": ""}).get('homepage', "")
    mod.authors = ', '.join(authors)
    mod.description = json_root.get('description', '')

    if "version" in mod.version:
        mod.version = _DEFAULT_VERSION


def __from_fabric_jar(mod: ModFile, zip_file: ZipFile) -> None:
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

    mod.icon = None
    icon_path = json_root.get('icon', None)
    try:
        if icon_path:
            f = zip_file.open(icon_path, 'r')
            mod.icon = f.read()
            f.close()
    except Exception as e:
        pass

    # 信息填充
    mod.name = json_root.get('name', _DEFAULT_NAME)
    mod.mod_id = json_root.get('id', '')
    mod.version = json_root.get('version', '')

    # 作者
    temp = json_root.get('authors', [])
    authors = []
    for i in temp:
        if isinstance(i, dict):
            if name := i.get('name', ''):
                authors.append(name)
        else:
            authors.append(i)
    # 内部 jar 文件
    jars: list[str] = [jar.get('file', '')
                       for jar in json_root.get('jars', [])]
    for jar_file in jars:
        if not jar_file:
            continue
        inner_mod = ModFile(file_name=jar_file)
        inner_mod.loader = 'fabric'
        inner_mod.parent = mod
        inner_zip = ZipFile(
            BytesIO(zip_file.open(jar_file).read()))
        inner_mod.__from_fabric_jar(inner_zip)
        mod.child_mods.append(inner_mod)

    # provides
    provides: list[str] = json_root.get('provides', [])
    for provide in provides:
        mod.provide_mods_id.append(str(provide))

    # 依赖设置
    for k, v in json_root.get('depends', {}).items():
        if k in ['minecraft', 'fabricloader', 'java', 'fabric']:
            continue
        if mod.included_mod_by_id(k):
            continue
        mod.dependencis.append(ModDepend(
            mod_id=k,
            mandatory=True,
            version_range=v
        ))

    mod.mc_version = json_root.get('depends', {}).get(
        'minecraft', _DEFAULT_MC_VERSION)

    mod.homepage = json_root.get(
        'contact', {"homepage": ""}).get('homepage', "")
    mod.authors = ', '.join(authors)
    mod.description = json_root.get('description', '')

    if "version" in mod.version:
        mod.version = _DEFAULT_VERSION


def __from_quilt_jar(mod: ModFile, zip_file: ZipFile) -> None:
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
    mod.mod_id = quilt_loader_info.get('id', _DEFAULT_MOD_ID)
    mod.version = quilt_loader_info.get('version', _DEFAULT_VERSION)

    # mc 版本
    mod.mc_version = _DEFAULT_MC_VERSION
    for dep in quilt_loader_info.get('depends', []):
        if isinstance(dep, str):
            continue
        if dep.get('id', '') == 'minecraft':
            mod.mc_version = dep.get('versions', _DEFAULT_MC_VERSION)
            break

    metadata = quilt_loader_info.get('metadata', {})
    if not metadata:
        return
    mod.name = metadata.get('name', _DEFAULT_NAME)
    mod.description = metadata.get('description', _DEFAULT_MOD_DESC)
    authors: list[str] = []
    authors.extend(metadata.get('contributors', {}).keys())
    authors.extend(metadata.get('authors', []))
    mod.authors = ', '.join(authors)
    mod.homepage = metadata.get('contact', {}).get('homepage', '')

    # 内部 jar
    jar_files: list[str] = quilt_loader_info.get('jars', [])
    for jar_file in jar_files:
        if not jar_file:
            continue
        inner_jar = ZipFile(
            BytesIO(zip_file.open(jar_file).read()))
        mod = ModFile(file_name=jar_file)
        mod.loader = 'quilt'
        mod.__from_quilt_jar(inner_jar)
        mod.parent = mod
        mod.child_mods.append(mod)

    # 依赖
    depends: list[dict] = quilt_loader_info.get('depends', [])
    for depend in depends:
        if isinstance(depend, str):
            depend_id = depend
            version_range = '*'
        else:
            depend_id: str = depend.get('id', '')
            version_range = depend.get('versions', '')
        if depend_id in ['minecraft', 'java', 'quilt', 'quilt_loader']:
            continue
        if mod.included_mod_by_id(depend_id):
            continue
        mod.dependencis.append(ModDepend(
            mod_id=depend_id,
            mandatory=True,
            version_range=version_range))

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
    mod.icon = icon

    # 检查 version 是否正确
    if "version" in mod.version:
        mod.version = _DEFAULT_VERSION


def __from_forge_jar(mod: ModFile, zip_file: ZipFile) -> None:
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
    mod.name = toml_mods.get('displayName', _DEFAULT_NAME)
    mod.mod_id = toml_mods.get('modId', _DEFAULT_MOD_ID)
    mod.version = toml_mods.get('version', _DEFAULT_VERSION)
    mod.description = toml_mods.get('description', _DEFAULT_MOD_DESC)
    mod.homepage = toml_mods.get('displayURL', "")
    mod.authors = toml_mods.get('authors', "")
    mod.icon = icon

    # 获取 mc 版本和依赖信息
    dependencies: list[dict] = toml_root.get(
        'dependencies', {}).get(mod.mod_id, [])
    mod.mc_version: str = _DEFAULT_MC_VERSION
    mod.dependencis = []
    for dep in dependencies:
        depend: ModDepend = ModDepend(
            mod_id=dep.get('modId', ''),
            mandatory=dep.get('mandatory', True),
            version_range=dep.get('versionRange', ''),
            ordering=dep.get('ordering', ''),
            side=dep.get('side', '')
        )
        if depend.mod_id == 'minecraft':
            mod.mc_version = dep.get('versionRange', _DEFAULT_MC_VERSION)
            continue
        if depend.mod_id in ['forge', 'java']:
            continue
        mod.dependencis.append(depend)

    # 从 MANIFEST.MF 文件补充缺失信息
    mf = {}
    if not mod.version or mod.version == _DEFAULT_VERSION or 'version' in mod.version.lower():
        mod.version = _mf(zip_file, mf).get(
            'Implementation-Version', _DEFAULT_VERSION)
    if not mod.name or mod.name == _DEFAULT_NAME:
        mod.name = _mf(zip_file, mf).get(
            'Implementation-Title', _DEFAULT_NAME)
    if not mod.mod_id or mod.mod_id == _DEFAULT_MOD_ID:
        mod.mod_id = _mf(zip_file, mf).get(
            'Specification-Title', _DEFAULT_MOD_ID)


def load_form_file(jar_file_path: str) -> ModFile:
    """从文件中读取为 mod
    """
    if not isfile(jar_file_path):
        raise ModLoadError(f"{jar_file_path} 不是一个文件")
    jar_zip = ZipFile(jar_file_path)
    return load_form_zipfile(jar_zip, full_file_path=abspath(jar_file_path))


def load_form_zipfile(jar: ZipFile, full_file_path: str, parent: ModFile | None = None) -> ModFile:
    """根据文件或ZipFile, 创建 ModInfo

    Raises:
        ModLoadError
    """

    result = ModFile(file_name=basename(full_file_path))
    result.full_file_path = abspath(full_file_path)
    loaders = get_loaders(jar)

    result.loader = ','.join(loaders)
    return result
    pass


def get_loaders(jar_zip: ZipFile) -> set[str]:
    """根据 jar 文件内的描述初步判断 mod 的加载器

    Args:
        zip_file (ZipFile): jar 文件

    Returns:
        list[str]: 加载器们
    """
    result: set[str] = set()
    file_list: list[str] = [i.filename for i in jar_zip.filelist]
    if _FABRIC_MOD_INFO_FILE in file_list:
        result.add('fabric')
    if _FORGE_MOD_INFO_FILE in file_list:
        result.add('forge')
    if _QUILT_MOD_INFO_FILE in file_list:
        result.add('quilt')
    if len(result) == 0:
        result.add('other')
    return result


if __name__ == '__main__':
    import os
    base = '/home/rika/980/Minecraft/.minecraft/versions/1.18.2-Forge_40.1.80/mods/'
    ls = os.listdir(base)
    for f in ls:
        file: str = join(base, f)
        if not isfile(file):
            continue
        loaders = get_loaders(ZipFile(file))
        if 'forge' in loaders:
            continue
        print(f)
        print("\t\t", loaders)
