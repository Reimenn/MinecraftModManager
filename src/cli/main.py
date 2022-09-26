from typing import Tuple
from cli.ModManagerCli import ModManagerCli


def _input2command(source: str) -> Tuple[str, list[str]]:
    input_split = user_input.split(' ')
    cmd: str = input_split[0].strip()
    args_source: str = ' '.join(input_split[1:]).strip()
    instr: bool = False
    str_start: str = ''
    args_list: list[str] = []
    buf: list[str] = []
    for c in args_source:
        if instr:
            if c in '\'\"' and c == str_start:
                instr = False
                continue
            buf.append(c)
        else:
            if c == ' ' and buf:
                args_list.append(''.join(buf))
                buf.clear()
                continue
            if c in '\'\"' and not buf:
                instr = True
                str_start = c
                continue
            buf.append(c)
    if buf:
        args_list.append(''.join(buf))

    return (cmd, args_list)


mmc = ModManagerCli()
while True:
    user_input = input()
    cmd, args = _input2command(user_input)
    try:
        result = mmc.call(cmd, args)
    except Exception as e:
        print("Error: " + str(e))
        continue

    for line in result:
        print(line)
