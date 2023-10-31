from abc import abstractmethod
from enum import Enum
import re
from typing import Generic, Optional, TypeVar, Union

from .stream import AssumedError, Stream


class ParsingFailed(AssumedError):
    pass


T  = TypeVar('T')
Result = Union[str, T, tuple[str, 'Result'], list['Result']]
TreeDesc = tuple[str, Union[str, list['TreeDesc']]]


class Parser(Generic[T]):
    @abstractmethod
    def parse(self, s: Stream, anchor: int) -> Result[T]:
        ...

    def describe(self, depth: int = 0, stack: Optional[set['Parser']] = None) -> TreeDesc:
        if stack is None:
            return self.describe(depth, set())
        elif self in stack:
            return self.__class__.__name__, "*looped*"
        else:
            try:
                stack.add(self)
                return self._describe(depth, stack)
            finally:
                stack.remove(self)

    @abstractmethod
    def _describe(self, depth: int, stack: set['Parser']) -> TreeDesc:
        ...

    def __call__(self, text: str):
        return self.parse(Stream(text), 0)


class Empty(Generic[T], Parser[T]):
    def parse(self, s: Stream, anchor: int) -> Result[T]:
        return []

    def _describe(self, depth: int, stack: set[Parser]) -> TreeDesc:
        return []


class Start(Generic[T], Parser[T]):
    def parse(self, s: Stream, anchor: int) -> Result[T]:
        if s.pos:
            raise ParsingFailed(s, 'Start unsatisfied')
        return []

    def _describe(self, depth: int, stack: set[Parser]) -> TreeDesc:
        return "Start"


class End(Generic[T], Parser[T]):
    def parse(self, s: Stream, anchor: int) -> Result[T]:
        if not s.at_end():
            raise ParsingFailed(s, 'End unsatisfied')
        return []

    def _describe(self, depth: int, stack: set[Parser]) -> TreeDesc:
        return "End"


class Terminal(Generic[T], Parser[T]):
    pass


class Token(Generic[T], Terminal[T]):
    def __init__(self, token: str):
        super().__init__()
        self.token = token

    def parse(self, s: Stream, anchor: int) -> Result[T]:
        with s:
            for c in self.token:
                if (ch := s.next()) != c:
                    raise ParsingFailed(s, f"Token mismatch '{self.token}' with {ch}")
            return self.token

    def _describe(self, depth: int, stack: set[Parser]) -> TreeDesc:
        return "Token", self.token


class Letter(Generic[T], Terminal[T]):
    def __init__(self, rex: str):
        super().__init__()
        self.rex = re.compile(rex)

    def parse(self, s: Stream, anchor: int) -> Result[T]:
        with s:
            if not self.rex.match(ch := s.next()):
                raise ParsingFailed(s, f"Letter mismatch '{ch}' != '{self.rex}'")
            return ch

    def _describe(self, depth: int, stack: set[Parser]) -> TreeDesc:
        return "Letter", self.rex


class QualifiedParser(Generic[T], Parser[T]):
    def __init__(self, content: Parser[T]):
        super().__init__()
        self.content = content


class Optional(Generic[T], QualifiedParser[T]):
    def parse(self, s: Stream, anchor: int) -> Result[T]:
        try:
            return self.content.parse(s, anchor)
        except ParsingFailed as e:
            return []

    def _describe(self, depth: int, stack: set[Parser]) -> TreeDesc:
        return "Optional", [self.content.describe(depth + 1, stack)]


class ZeroOrMore(Generic[T], QualifiedParser[T]):
    def parse(self, s: Stream, anchor: int) -> Result[T]:
        result = []
        while not s.at_end():
            try:
                result.append(self.content.parse(s, anchor))
            except ParsingFailed as e:
                break
        return result

    def _describe(self, depth: int, stack: set[Parser]) -> TreeDesc:
        return "ZeroOrMore", [self.content.describe(depth + 1, stack)]


class OneOrMore(Generic[T], ZeroOrMore[T]):
    def parse(self, s: Stream, anchor: int) -> Result[T]:
        result = super().parse(s, anchor)
        if len(result) == 0:
            raise ParsingFailed(s, 'OneOrMore unsatisfied')
        return result

    def _describe(self, depth: int, stack: set[Parser]) -> TreeDesc:
        return "OneOrMore", [self.content.describe(depth + 1, stack)]


class AndPredicate(Generic[T], QualifiedParser[T]):
    def parse(self, s: Stream, anchor: int) -> Result[T]:
        with s:
            self.content.parse(s, anchor)
            s.rewind()
            return []

    def _describe(self, depth: int, stack: set[Parser]) -> TreeDesc:
        return "AndPredicate", [self.content.describe(depth + 1, stack)]


class NotPredicate(Generic[T], QualifiedParser[T]):
    def parse(self, s: Stream, anchor: int) -> Result[T]:
        with s:
            try:
                self.content.parse(s, anchor)
            except ParsingFailed as e:
                s.rewind()
                return []
            raise ParsingFailed(s, 'NotPredicate unsatisfied.')

    def _describe(self, depth: int, stack: set[Parser]) -> TreeDesc:
        return "NotPredicate", [self.content.describe(depth + 1, stack)]


class Choice(Generic[T], Parser[T]):
    def __init__(self, *choices: Parser):
        super().__init__()
        self.choices = choices

    def parse(self, s: Stream, anchor: int) -> Result[T]:
        for choice in self.choices:
            try:
                return choice.parse(s, anchor)
            except ParsingFailed as e:
                pass
        else:
            raise ParsingFailed(s, "Choice mismatch")

    def update(self, *choices: Parser):
        self.choices = choices
        return self

    def _describe(self, depth: int, stack: set[Parser]) -> TreeDesc:
        return "Choice", [choice.describe(depth + 1, stack) for choice in self.choices]


class Producer(Generic[T]):
    @abstractmethod
    def produce(self, parsed: Result[T]) -> Result[T]:
        ...


class DefaultProducer(Generic[T], Producer[T]):
    def produce(self, parsed: Result[T]) -> Result[T]:
        return parsed


class Sequence(Generic[T], Parser[T]):

    class Layout(Enum):
        free = 0    # %
        inline = 1  # ~
        indent = 2  # ^
        keep = 3    # =
        nosp = 4    # $

        def skip_air(self, s: Stream):
            if self == self.nosp:
                return

            if self == self.inline:
                while not s.at_end():
                    c = s.next()
                    if not c.isspace() or c == "\n":
                        s.stepback()
                        return
            else:
                while not s.at_end():
                    c = s.next()
                    if not c.isspace():
                        s.stepback()
                        return

        def adjust(self, s: Stream, anchor: int):

            if self == self.indent:
                if s.shift <= anchor:
                    raise ParsingFailed(s, 'Not indented.')
                return s.shift

            if self == self.keep:
                if anchor != s.shift:
                    raise ParsingFailed(s, 'Not the indentation kept.')
                return s.shift

            return anchor

    def __init__(self, *children: tuple['Parser', Layout, str], producer: Optional[Producer[T]] = None):
        super().__init__()
        self.producer = producer or DefaultProducer[T]()
        self.children = children

    def update(self, *children: tuple['Parser', Layout, str], producer: Optional[Producer[T]] = None):
        self.producer = producer or self.producer or DefaultProducer[T]()
        self.children = children or self.children
        return self

    def parse(self, s: Stream, anchor: int) -> Result[T]:
        result = []
        with s:
            for child, layout, tag in self.children:
                layout.skip_air(s)
                parsed = child.parse(s, layout.adjust(s, anchor))
                result.append((tag, parsed) if tag else parsed)
        return self.producer.produce(result)

    def _describe(self, depth: int, stack: set[Parser]) -> TreeDesc:
        return "Sequence", [(child.describe(depth + 1, stack) if layout in (self.Layout.free, self.Layout.nosp) and not tag else (child.describe(), layout, tag))
                            for child, layout, tag in self.children]


def print_tree_desc(node: TreeDesc, depth: int = 0):
    label, body = node
    if isinstance(body, str) or isinstance(body, re.Pattern):
        print("    "  * depth + f"{label}: {body}")
    else:
        print("    "  * depth + f"{label}:")
        for child in body:
            print_tree_desc(child, depth + 1)


