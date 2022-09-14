import dataclasses


@dataclasses.dataclass
class WebMod(object):
    name: str = ''
    image_url: str = ''
    mod_id: str = ''
    loader: str = ''
    later_version: str = ''
    mod_type: str = ''
    location_name: str = ''
    descrption: str = ''
    download_link: str = ''
