def version_cmp(v1: str, v2: str) -> int:
    """两个版本号互相做比较
    """
    v1 = v1.strip('. ')
    v2 = v2.strip('. ')
    v1s = v1.split('.')
    v1l = len(v1s)
    v2s = v2.split('.')
    v2l = len(v2s)
    i = 0
    while True:
        if i >= v1l and i >= v2l:
            return 0
        if i >= v1l:
            return -1
        if i >= v2l:
            return 1
        a = v1s[i]
        b = v2s[i]
        if a == 'x' and b == 'x':
            return 0
        if a == 'x':
            return -1
        if b == 'x':
            return 1
        if int(a) > int(b):
            return 1
        if int(a) < int(b):
            return -1
        i += 1


def in_version_forge(version: str, range: str) -> bool:
    """判断一个游戏版本是否在一个 forge 格式的版本范围之内
    """
    if range.startswith('未知'):
        return False
    if int(version.split('.')[0]) > 1:
        version = '1.' + version
    print(f"{version=},   {range=}")
    startin = range.startswith('[')
    endin = range.endswith(']')
    versions = range[1:-1].split(',')
    if len(versions) == 1:
        return version_cmp(versions[0], version) == 0
    if len(versions[0]) == 0:
        versions[0] = '0'
    if len(versions[1]) == 0:
        versions[1] = '99999999'
    l = version_cmp(version, versions[0])
    s = version_cmp(version, versions[1])
    if l == 0 and startin:
        return True
    if s == 0 and endin:
        return True
    if l == 1 and s == -1:
        return True
    return False