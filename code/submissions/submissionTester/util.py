import sys
from contextlib import contextmanager
from os import devnull
from os.path import join, dirname
from threading import Thread
from typing import Union, List, Tuple

from lxml import etree
from lxml.etree import _ElementTree, _Element

from test_types.challenge_test import ChallengeTestAIStat

XSD_FILE_PATH = join(dirname(__file__), "..", "..", "drivebuild", "simnode", "schemes", "drivebuild.xsd")
SCHEMA_ROOT = etree.parse(XSD_FILE_PATH)
SCHEMA = etree.XMLSchema(SCHEMA_ROOT)
PARSER = etree.XMLParser(schema=SCHEMA, recover=False, remove_comments=True)
SCHEMALESS_PARSER = etree.XMLParser(recover=False, remove_comments=True)
NAMESPACES = {
    "db": "http://drivebuild.com"
}


def xpath(xml_tree: Union[_Element, _ElementTree], expression: str) -> Union[List[_Element], _ElementTree]:
    return xml_tree.xpath(expression, namespaces=NAMESPACES)


def get_tag_name(node: _Element) -> str:
    return node.tag.split("}")[1] if "}" in node.tag else node.tag


def is_dbe(root: _ElementTree) -> bool:
    return get_tag_name(root.getroot()) == "environment"


def is_dbc(root: _ElementTree) -> bool:
    return get_tag_name(root.getroot()) == "criteria"


@contextmanager
def silence_stdout():
    new_target = open(devnull, "w")
    old_target = sys.stdout
    sys.stdout = new_target
    try:
        yield new_target
    finally:
        sys.stdout = old_target


def join_all(threads: Union[List[Thread], List[Tuple[Thread, ChallengeTestAIStat]]], timeout: float) \
        -> List[Thread]:
    """
    Waits for all given threads the given amount of time trying to join them.
    :param threads: The threads to join.
    :param timeout: The timeout for all threads to finish (in seconds).
    :return: The list of threads that could not be joined within the given timeout.
    """
    # NOTE Based on https://stackoverflow.com/a/35342348/4863098
    from time import time, sleep
    if len(threads) > 0:
        contains_stats = isinstance(threads[0], Tuple)
        start_time = current_time = time()
        while current_time <= (start_time + timeout):
            if contains_stats:
                any_alive = any(thread.is_alive() or not stat.finished for thread, stat in threads)
            else:
                any_alive = any(thread.is_alive() for thread in threads)
            if any_alive:
                sleep(0.1)
                current_time = time()
            else:
                break
        return list(filter(lambda t: t.is_alive(), map(lambda t: t[0] if contains_stats else t, threads)))
    else:
        return []
