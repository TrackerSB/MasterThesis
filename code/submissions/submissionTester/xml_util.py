from logging import getLogger

from pathlib import Path
from typing import Optional, Union, List

from lxml.etree import _ElementTree, _Element
_logger = getLogger("SubmissionTester.XmlUtil")


def parse_xml(path: Path) -> Optional[_ElementTree]:
    from util import SCHEMALESS_PARSER
    from lxml.etree import parse
    try:
        tree = parse(path.as_posix(), SCHEMALESS_PARSER)  # May throw XMLSyntaxException
    except Exception as ex:
        _logger.warning("Parsing of \"" + path.as_posix() + "\" failed due to " + str(ex))
        tree = None
    return tree


def findall(node: Union[_Element, _ElementTree], expression: str) -> List[_Element]:
    from util import NAMESPACES
    return node.findall(expression, namespaces=NAMESPACES)


def find(node: Union[_Element, _ElementTree], expression: str) -> _Element:
    from util import NAMESPACES
    return node.find(expression, namespaces=NAMESPACES)
