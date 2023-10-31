from abc import abstractmethod
import re
from typing import Generic, Optional, TypeVar, Union

from .parser import Result, TreeDesc, Parser, Stream, Layout, choice, sequence, start, eof
from .builder import Builder, Context, Attribute, Element


T = TypeVar('T')


class ParserRef(Generic[T], Parser[T]):
    def __init__(self, parser_name: str):
        super().__init__()
        self.parser_ref = CompilerCompiler.make_ref(parser_name)

    def parse(self, s: Stream, anchor: int) -> Result[T]:
        return self.parser_ref().parse(s, anchor)

    def _describe(self, depth: int, stack: set[Parser]) -> TreeDesc:
        return self.parser_ref().describe(depth, stack)


Compiled = Union[Element, Attribute, str]


class AtomicCompiler(Parser[Compiled]):
    def __init__(self, parser: Parser[Compiled], builder: Builder):
        super().__init__()
        self.parser = parser
        self.builder = builder

    def parse(self, s: Stream, anchor: int) -> Result[Compiled]:
        return self.builder.build(Context(init=self.parser.parse(s, anchor)))

    def _describe(self, depth: int, stack: set[Parser]) -> TreeDesc:
        return self.parser.describe(depth, stack)


class SpecializedCompiler(Generic[T], Parser[T]):
    def __init__(self, name: str, mappings: list[Parser[Compiled]]):
        super().__init__()
        self.name = name
        self.compiler = choice(*mappings)

    @abstractmethod
    def _type_check(self, s: Stream, result: Compiled):
        ...

    def parse(self, s: Stream, anchor: int) -> T:
        result = self.compiler.parse(s, anchor)
        self._type_check(s, result)
        return result

    def _describe(self, depth: int, stack: set[Parser]) -> TreeDesc:
        return self.compiler.describe(depth, stack)


class TextCompiler(SpecializedCompiler[str]):
    def _type_check(self, s: Stream, result: Compiled):
        try:
            assert isinstance(result, str)
        except AssertionError:
            print(f'ERROR: "{self.name}" is declared as text rule but it builds "{result}".')
            raise


class AttributeCompiler(SpecializedCompiler[Attribute]):
    def _type_check(self, s: Stream, result: Compiled):
        assert isinstance(result, Attribute), f'ERROR: "{self.name}" is declared as attribute rule but it builds "{result}".'


class ElementCompiler(SpecializedCompiler[Element]):
    def _type_check(self, s: Stream, result: Compiled):
        assert isinstance(result, Element), f'ERROR: "{self.name}" is declared as element rule but it builds "{result}".'


class RootCompiler(SpecializedCompiler[Element]):
    def __init__(self, name: str, mappings: list[Parser[Compiled]]):
        super().__init__(name, [sequence(start(), choice(*mappings), eof(), producer=lambda parsed: parsed[1])])

    def _type_check(self, s: Stream, result: Compiled):
        assert isinstance(result, Element), f'ERROR: "{self.name}" is declared as element rule but it builds "{result}".'

    def parse(self, s: Stream, anchor: int) -> Element:
        return super().parse(s, anchor)


class CompilerCompiler:
    compilers: dict[str, Parser[Compiled]] = {}
    root: Optional[RootCompiler] = None

    @classmethod
    def register(cls, name: str, compiler: SpecializedCompiler[Compiled]):
        assert name not in cls.compilers
        cls.compilers[name] = compiler
        if isinstance(compiler, RootCompiler):
            assert not cls.root, "ERROR: root rule is already defined."
            cls.root = compiler
        return compiler

    @classmethod
    def lookup(cls, name: str):
        return cls.compilers[name]

    @classmethod
    def make_ref(cls, name: str):
        return (lambda compilers: (lambda: compilers.get(name)))(cls.compilers)

    @classmethod
    def reset(cls) -> Optional[RootCompiler]:
        try:
            return cls.root
        finally:
            cls.compilers = {}
            cls.root = None


