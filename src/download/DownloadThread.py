import abc
from threading import Thread
from typing import Callable

import httpx

_tCallback = Callable[[httpx.Response], None]


class DownloadingInNewThread(object):
    def __init__(self, callback: _tCallback) -> None:
        self.callback: _tCallback = callback
        self.cancel: bool = False

        self.thread: Thread = Thread(target=self.downloading_in_new_thread)
        self.thread.start()

    @abc.abstractmethod
    def downloading_in_new_thread(self):
        pass

    def Cancel(self):
        self.cancel = True

    def commit(self, response: httpx.Response):
        if not self.cancel:
            self.callback(response)


class Get(DownloadingInNewThread):
    def __init__(self, url: str, params: dict[str, str], callback: _tCallback) -> None:
        super().__init__(callback)
        self.params: dict[str, str] = params
        self.url: str = url

    def downloading_in_new_thread(self):
        response: httpx.Response = httpx.get(self.url, params=self.params)
        self.commit(response)
