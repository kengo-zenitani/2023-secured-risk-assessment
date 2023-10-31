from pprint import pprint
from .compiler.parser import ParsingFailed, Stream


def expect_ok(parser, code, answer):
    try:
        result = parser.parse(Stream(code), 0)
        assert result == answer
    except ParsingFailed as e:
        print([e.pos, e.shift, e])


def expect_ng(parser, code):
    try:
        parser.parse(Stream(code), 0)
        assert "Error!"
    except ParsingFailed as e:
        pass


def echo(d):
    pprint(d)
    return d


