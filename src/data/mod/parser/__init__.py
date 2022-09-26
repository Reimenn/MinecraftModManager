from data.mod.parser.FabricModParser import FabricModParser
from data.mod.parser.QuiltModParser import QuiltModParser
from data.mod.parser.ForgeModParser import ForgeModParser
from data.mod.parser.ModParserBase import ModParserBase

PARSERS: list[type[ModParserBase]] = [
    FabricModParser,
    ForgeModParser,
    QuiltModParser
]
