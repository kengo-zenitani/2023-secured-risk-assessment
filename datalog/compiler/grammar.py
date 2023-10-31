from typing import Generic, Union, TypeVar
from .parser import (
    Stream, Result, Parser, TreeDesc, Token, Letter, Translator, Layout,
    gapless, sequence, choice, optional, zero_or_more, one_or_more, start, eof, _,
    flatten, take)
from .builder import (
    Builder, Attribute, Element,
    StringBuilder, TextBuilder, ConcatenatedTextBuilder, AttributeBuilder, ElementBuilder,
    Dereference, LeftFolding, RightFolding, ElementOnly, AsString, TreeBuilder)
from .compiler import CompilerCompiler, Compiled, AtomicCompiler, TextCompiler, AttributeCompiler, ElementCompiler, RootCompiler


T = TypeVar('T')


class SimpleString:
    escaped_char = gapless("\\", Letter("."), producer=lambda parsed: parsed[1])
    single_quoted_string = gapless("'", one_or_more(choice(escaped_char, Letter("[^']"))), "'")
    double_quoted_string = gapless('"', one_or_more(choice(escaped_char, Letter('[^"]'))), '"')

    string = sequence(choice(single_quoted_string, double_quoted_string), producer=lambda parsed: Token(''.join(flatten(parsed))[1:-1]))


class RexString:

    def rex_element_builder(parsed):
        if len(parsed[1]) == 0:
            return parsed[0]
        else:
            qualifier = ''.join(flatten(parsed[1]))

            if qualifier == '?':
                return optional(parsed[0])

            if qualifier == '*':
                return zero_or_more(parsed[0])

            if qualifier == '+':
                return one_or_more(parsed[0])

            raise ValueError(f"Unknown qualifier {qualifier} specified.")

    escaped_char = gapless("\\", Letter("."), producer=lambda parsed: Token(parsed[1]))
    secured_char = gapless(Letter("[^][)(|?*+/]"), producer=lambda parsed: Token(parsed[0]))

    char_spec = one_or_more(choice(gapless("\\", Letter(".")), Letter("[^]]")))
    char_class = gapless("[", choice(["^]", zero_or_more(char_spec)], [optional("^"), one_or_more(char_spec)]), "]", producer=lambda parsed: Letter(''.join(flatten(parsed))))

    rex_char = choice(escaped_char, secured_char, char_class)

    rex_pattern = gapless()
    rex_factor = choice(gapless('(', rex_pattern, ')', producer=lambda parsed: parsed[1]), rex_char)
    rex_element = gapless(rex_factor, optional(choice('?', '*', '+')), producer=rex_element_builder)
    rex_sequence = gapless(one_or_more(rex_element), producer=lambda parsed: gapless(*flatten(parsed)))
    rex_pattern.update(*_(rex_sequence, zero_or_more(gapless('|', rex_sequence))), producer=Translator(lambda parsed: choice(*flatten(parsed)[0::2])))

    class Parser(Generic[T], Parser[T]):
        def __init__(self, parser: Parser[T]):
            super().__init__()
            self.parser = parser

        def parse(self, s: Stream, anchor: int) -> Result[T]:
            return ''.join(flatten(self.parser.parse(s, anchor)))

        def _describe(self, depth: int, stack: set[Parser]) -> TreeDesc:
            return self.parser.describe(depth, stack)

    rex_string = gapless('/', rex_pattern, '/', producer=lambda parsed: RexString.Parser(parsed[1]))


class Head:

    def build_term(parsed: list[Result[T]]):
        _name, _parser, _layout, _repetition = parsed

        from .compiler import ParserRef
        parser = ParserRef[T](_parser) if isinstance(_parser, str) else _parser

        _name = ''.join(flatten(_name))
        name = _name[:-1] if _name else ''

        _layout = ''.join(flatten(_layout))
        layout = Layout.free if not _layout else {
            '%': Layout.free,
            '~': Layout.inline,
            '^': Layout.indent,
            '=': Layout.keep,
            '$': Layout.nosp,
        }[_layout]

        _repetition = ''.join(flatten(_repetition))
        if _repetition == '?':
            parser = optional(parser)
        elif _repetition == '*':
            parser = zero_or_more(parser)
        elif _repetition == '+':
            parser = one_or_more(parser)

        return (parser, layout, name)

    string = SimpleString.string
    rex_string = RexString.rex_string

    name = rex_string("/[A-Za-z_][0-9A-Za-z_]*/")

    element = sequence()

    rule = name
    layout = choice('%', '~', '^', '=', '$')
    repetition = choice('?', '*', '+')
    sub_element = sequence('(', element, ')', producer=lambda parsed: parsed[1])
    term = sequence(optional([name, '.']), choice(string, rex_string, rule, sub_element), optional(layout), optional(repetition), producer=build_term)
    pattern = sequence(one_or_more(term), producer=lambda parsed: sequence(*parsed[0]))

    element.update(*_(pattern, zero_or_more(['|', pattern])), producer=Translator(lambda parsed: choice(*flatten(parsed)[0::2])))

    head = element


class Body:

    def tag_check(start_tag: ElementBuilder, end_tag: ElementBuilder):
        assert start_tag.tagName == end_tag.tagName
        return True

    def wrap_with_modifier(deref: Builder, modifier: Union[str, TreeBuilder, None] = None):

        if not modifier:
           return deref

        if modifier == 'foldl':
            return LeftFolding(deref)

        if modifier == 'foldr':
            return RightFolding(deref)

        if modifier == 'elem_only':
            return ElementOnly(deref)

        if modifier == 'as_str':
            return AsString(deref)

        if isinstance(modifier, TreeBuilder):
            return modifier.bind(deref)

        raise ValueError(value)

    string = SimpleString.string
    rex_string = RexString.rex_string

    name = Head.name

    content = choice()

    name_value = sequence(name, producer=lambda parsed: TextBuilder(parsed[0]))
    string_value = sequence(string, producer=lambda parsed: TextBuilder(parsed[0].token))

    filter = choice('foldl', 'foldr', 'elem_only', 'as_str')
    mapper = sequence(name, '=>', content, producer=lambda parsed: TreeBuilder(parsed[0], parsed[2]))
    modifier = sequence(':', choice(filter, mapper), producer=lambda parsed: take(parsed[1]))
    refname = rex_string("/[A-Za-z_][0-9A-Za-z_]*(.[A-Za-z_][0-9A-Za-z_]*)*|$$/")
    block = sequence('{', optional("*"), refname, optional(modifier), '}',
                     producer=lambda parsed: Body.wrap_with_modifier(Dereference(parsed[2], bool(parsed[1])), *flatten(parsed[3])))

    text = sequence(one_or_more(string_value), producer=lambda parsed: ConcatenatedTextBuilder(source=flatten(parsed)))

    mixed_text = sequence(choice(text, block), one_or_more(choice(text, block)), producer=lambda parsed: ConcatenatedTextBuilder(source=flatten(parsed)))

    attr = sequence('[', choice(name_value, block), '=', choice(string_value, block), ']', producer=lambda parsed: AttributeBuilder(name=take(parsed[1]), value=take(parsed[3])))

    attrs = zero_or_more(
        choice(
            sequence(choice(name_value, block), '=', choice(string_value, block), producer=lambda parsed: AttributeBuilder(name=take(parsed[0]), value=take(parsed[2]))),
            sequence('[', name, ']', producer=lambda parsed: Dereference(parsed[1]))))

    start_tag = sequence('<', name, attrs, '>', producer=lambda parsed: ElementBuilder(tagName=parsed[1], attrBuilders=parsed[2]))
    end_tag = sequence('</', name, '>', producer=lambda parsed: ElementBuilder(tagName=parsed[1]))
    elem = sequence(start_tag, zero_or_more(content), end_tag, producer=lambda parsed: Body.tag_check(parsed[0], parsed[2]) and parsed[0].set_children(flatten(parsed[1])))
    single_elem = sequence('<', name, attrs, '/>', producer=lambda parsed: ElementBuilder(tagName=parsed[1], attrBuilders=parsed[2]))
    content.update(single_elem, elem, text, block)

    body = choice(single_elem, elem, attr, text, mixed_text, block)


class Main:

    def build_compiler(type_spec: str, name: str, mappings: list[AtomicCompiler]) -> Parser[Compiled]:
        return CompilerCompiler.register(name, {
            'text': TextCompiler,
            'attr': AttributeCompiler,
            'elem': ElementCompiler,
            'root': RootCompiler,
        }[type_spec](name, mappings))

    name = Head.name
    head = Head.head
    body = Body.body

    type_spec = choice("text", "attr", "elem")
    mapping = sequence(head, '->', body, ';', producer=lambda parsed: AtomicCompiler(parser=parsed[0], builder=parsed[2]))
    decl = sequence(type_spec, name, ":", one_or_more(mapping), producer=lambda parsed: Main.build_compiler(type_spec=parsed[0], name=parsed[1], mappings=parsed[-1]))
    root_decl = sequence("root", ":", one_or_more(mapping), producer=lambda parsed: Main.build_compiler(type_spec="root", name="<root>", mappings=parsed[-1]))

    grammar = sequence(start(), one_or_more(choice(decl, root_decl)), eof())


def compiler(grammar: str) -> Parser[Compiled]:
    CompilerCompiler.reset()
    Main.grammar(grammar)
    return CompilerCompiler.reset()


