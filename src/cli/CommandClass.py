from typing import Any, Callable, Iterable


class CommandBase(object):
    def __init__(self) -> None:
        self.commands: dict[str, Callable[..., Iterable[str]]] = {}
        self.sub_command_class: dict[str, CommandBase] = {}
        self.init_commands()

    def init_commands(self):
        """初始化命令们，这会在 CommandBase 中自动调用。
        """
        for k, v in self.__class__.__dict__.items():
            if not isinstance(v, Callable):
                continue
            if k.startswith('cmd_'):
                command_name = '_'.join(k.split('_')[1:])
                self.commands[command_name] = getattr(self, v.__name__)

    def call(self, cmd: str, args: list[str]) -> Iterable[str]:
        """调用一个命令并返回输出内容迭代器
        """
        if cmd in self.commands:
            return self.commands[cmd](*args)
        if cmd in self.sub_command_class:
            return self.sub_command_class[cmd].call(args[0],args[1:])
        raise Exception("未知命令：" + cmd)
