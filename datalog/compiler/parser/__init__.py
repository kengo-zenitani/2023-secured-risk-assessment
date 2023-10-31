from typing import Callable, Generic, TypeVar
from .parser import (
    Producer, Result, TreeDesc, ParsingFailed,
    Parser, Token, Letter, Optional, ZeroOrMore, OneOrMore, AndPredicate, NotPredicate, Choice, Sequence, Start, End)
from .stream import Stream


T = TypeVar('T')
Layout = Sequence.Layout


class Translator(Generic[T], Producer[T]):
    def __init__(self, producer: Callable[[Result[T]], Result[T]]):
        super().__init__()
        self.producer = producer

    def produce(self, parsed: Result[int]) -> Result[int]:
        return self.producer(parsed)


def _expand_children(*rules, default_layout = Sequence.Layout.free):

    def normalize(rule):
        if isinstance(rule, str):
            return (Token(rule), default_layout, "")

        if isinstance(rule, tuple):
            if len(rule) == 1:
                return (*rule, default_layout, "")
            elif len(rule) == 2:
                return (*rule, "")
            else:
                return rule
        else:
            return (rule, default_layout, "")

    return [normalize(rule) for rule in rules]


def _(*rules):
    return _expand_children(*rules)


def sequence(*rules, producer = None):
    if producer:
        producer = Translator(producer)
    return Sequence(*_expand_children(*rules), producer=producer)


def gapless(*rules, producer = None):
    if producer:
        producer = Translator(producer)
    return Sequence(*_expand_children(*rules, default_layout=Sequence.Layout.nosp), producer=producer)


def _expand_rules(*rules):

    def normalize(rule):
        if isinstance(rule, str):
            return Token(rule)
        elif isinstance(rule, list):
            return sequence(*rule)
        else:
            return rule

    return [normalize(rule) for rule in rules]


def choice(*rules):
    return r[0] if 1 == len(r := _expand_rules(*rules)) else Choice(*r)


def optional(*rules):
    return Optional(*_expand_rules(*rules))


def zero_or_more(*rules):
    return ZeroOrMore(*_expand_rules(*rules))


def one_or_more(*rules):
    return OneOrMore(*_expand_rules(*rules))


def and_pred(*rules):
    return AndPredicate(*_expand_rules(*rules))

def not_pred(*rules):
    return NotPredicate(*_expand_rules(*rules))


def start():
    return (Start(), Sequence.Layout.nosp, "")

def eof():
    return (End(), Sequence.Layout.free, "")


def flatten(l, limit = -1):
    def _flatten(l, limit):
        if isinstance(l, list):
            for el in l:
                if limit != 0:
                    yield from _flatten(el, limit - 1)
                else:
                    yield el
        else:
            yield l

    return list(_flatten(l, limit))


def take(composite):
    decomposed = flatten(composite)
    assert len(decomposed) == 1
    return decomposed[0]


