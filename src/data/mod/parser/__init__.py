from .FabricModParser import FabricModParser
from .ModParserBase import ModParserBase

PARSERS: list[type[ModParserBase]] = [
    FabricModParser
]
