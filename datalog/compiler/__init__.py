from typing import Any
from xml.dom.minidom import Node
from .grammar import compiler


class ProgramVisitor:
    def visit(self, node: Node, args: list[Any]):
        if node.nodeType == Node.ELEMENT_NODE:
            attrs = dict(node.attributes.items())
            if handler := getattr(self, node.tagName.lower(), None):
                return handler(attrs=attrs, children=args)
        return args


class Interpreter:
    def __init__(self, visitor: ProgramVisitor):
        self.visitor = visitor

    def interpret(self, node: Node):
        args = []
        for child in node.childNodes:
            if (arg := self.interpret(child)) is not None:
                args.append(arg)

        return self.visitor.visit(node, args)


