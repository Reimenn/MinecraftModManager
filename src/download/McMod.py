from download.WebMod import WebMod
from download.DownloadThread import Get
from bs4 import BeautifulSoup
from bs4.element import Tag

FUCK_IMPORT = False
if FUCK_IMPORT:
    import httpx

MCMOD_SEARCH_URL: str = 'https://www.mcmod.cn/modlist.html'



def parse_search_page(source: str):
    root: Tag = BeautifulSoup(source, 'html.parser')
    mod_blocks: list[Tag] = root.find_all('div', **{'class': 'modlist-block'})
    for block in mod_blocks:
        block.find()


class McModSearchFilter(object):
    CATEGORY_科技 = '1'

    PLATFORM_Java = '1'

    LOADER_Forge = '1'

    STATUS_活跃 = '1'

    MODE_仅客户端 = '1'

    SORT_CreateTime = 'createtime'
    SORT_LastEditTime = 'lastedittime'

    def __init__(self,
                 category: str = '',
                 mc_version: str = '',
                 platform: str = '',
                 loader: str = '',
                 status: str = '',
                 mode: str = '',
                 sort: str = '') -> None:
        self.category: str = category
        self.mc_version: str = mc_version
        self.platform: str = platform
        self.loader: str = loader
        self.status: str = status
        self.mode: str = mode
        self.sort: str = sort

    def to_dict(self) -> dict[str, str]:
        result = {
            'category': self.category,
            'mcver': self.mc_version,
            'platform': self.platform,
            'api': self.loader,
            'status': self.status,
            'mode': self.mode,
            'sort': self.sort,
        }
        for k in result.keys():
            if not result[k]:
                del result[k]
        return result


def _search_mod_callback(response: 'httpx.Response'):
    if response.status_code != 200:
        return


def search_mod(page: int, filter: McModSearchFilter) -> list[WebMod]:
    result: list[WebMod] = []
    params = filter.to_dict()
    params['page'] = str(page)
    Get(MCMOD_SEARCH_URL, params=params,
        callback=_search_mod_callback)
    return result


if __name__ == 'main':
    search_mod(1, McModSearchFilter(
        mc_version='1.16.5',
        mode='1',
        loader='1',
    ))
