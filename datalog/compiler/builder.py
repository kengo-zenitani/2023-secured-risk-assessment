from abc import abstractmethod
from typing import Any, Optional, Union
from xml.dom.minidom import Document, Element
from .parser import flatten


class Attribute:
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

    def unpack(self):
        return self.name, self.value


MixedTree = Union[str, Element, 'Context', tuple[str, 'MixedTree'], list['MixedTree']]


class Context:
    def __init__(self, parent: Optional['Context'] = None, init: Optional[list[MixedTree]] = None):
        self.document = Document() if not parent else parent.document
        self.parent = parent
        self.content = init or []
        self.dict = {'$$': self.content}
        for item in self.content:
            if isinstance(item, tuple):
                self.put(*item)

    def __iter__(self):
        return iter(self.content)

    def put(self, key: str, value: MixedTree) -> 'Context':
        value = Context(init=value) if isinstance(value, list) else value
        self.dict[key] = value
        if isinstance(value, Context):
            value.parent = self
        return self

    def get(self, key: str, default: Any = None) -> MixedTree:
        subkeys = key.split('.')
        scope = self.dict
        while subkeys:
            value = scope.get(subkeys.pop(0), [])
            if isinstance(value, Context):
                scope = value
            elif subkeys:
                raise KeyError(key)

        return self.parent.get(key) if not value and self.parent else value

    def flatten(self, key: str) -> MixedTree:
        return flatten(subject.content if (subject := self.get(key)) and isinstance(subject, Context) else subject)

    def describe(self):
        return "Context", {key: (value.describe() if isinstance(value, Context) else value) for key, value in self.dict.items()}


class Builder:
    @abstractmethod
    def build(self, context: Context) -> Union[str, Attribute, Element]:
        ...


class StringBuilder(Builder):
    def build(self, context: Context) -> str:
        ...


class TextBuilder(StringBuilder):
    def __init__(self, value: str):
        self.value = value

    def build(self, context: Context) -> str:
        return self.value


class ConcatenatedTextBuilder(StringBuilder):
    def __init__(self, source: list[Union[str, StringBuilder]]):
        self.source = source

    def build(self, context: Context) -> str:
        return ''.join((b if isinstance(b, str) else b.build(context)) for b in self.source)


class AttributeBuilder(Builder):
    def __init__(self, name: Builder, value: Builder):
        self.name = name
        self.value = value

    def build(self, context: Context) -> Attribute:
        name, value = self.name.build(context), self.value.build(context)
        assert isinstance(name, str) and isinstance(value, str)
        return Attribute(name, value)


class ElementBuilder(Builder):
    def __init__(self, tagName, attrBuilders: list[AttributeBuilder] = []):
        self.tagName = tagName
        self.attrBuilders = attrBuilders
        self.childBuilders = []

    def set_children(self, children: list[Union[Builder]]) -> 'ElementBuilder':
        assert all(isinstance(c, Builder) for c in children)
        self.childBuilders = children.copy()
        return self

    def build(self, context: Context) -> Element:
        e = context.document.createElement(tagName=self.tagName)
        for attr_builder in self.attrBuilders:
            name, value = attr_builder.build(context).unpack()
            if name:
                assert isinstance(name, str) and isinstance(value, str)
                e.setAttribute(name, value)

        def append_child(child):
            if isinstance(child, str):
                e.appendChild(context.document.createTextNode(child))
            elif isinstance(child, Element):
                e.appendChild(child)
            elif isinstance(child, list):
                for sub_child in child:
                    append_child(sub_child)
            else:
                raise ValueError(child)

        for child_builder in self.childBuilders:
            if child := child_builder.build(context):
                append_child(child)

        return e


class Dereference(Builder):
    def __init__(self, key: str, flatten: bool = False):
        self.key = key
        self.flatten = flatten

    def build(self, context: Context) -> Union[str, Attribute, Element]:
        return context.get(self.key) if not self.flatten else context.flatten(self.key)


class LeftFolding(Builder):
    def __init__(self, deref: Builder):
        self.deref = deref

    def build(self, context: Context) -> Element:
        return ''.join(reversed(self.deref.build(context)))


class RightFolding(Builder):
    def __init__(self, deref: Builder):
        self.deref = deref

    def build(self, context: Context) -> Element:
        return self.deref.build(context) * 2


class ElementOnly(Builder):
    def __init__(self, deref: Builder):
        self.deref = deref

    def build(self, context: Context) -> list[Element]:
        return [item for item in self.deref.build(context) if isinstance(item, Element)]


class AsString(Builder):
    def __init__(self, deref: Builder):
        self.deref = deref

    def build(self, context: Context) -> str:
        return ''.join(flatten(self.deref.build(context)))


class TreeBuilder(Builder):
    def __init__(self, label: str, content: Builder):
        self.label = label
        self.content = content

    def bind(self, deref: Builder) -> 'TreeBuilder':
        self.deref = deref
        return self

    def build(self, context: Context) -> MixedTree:
        subject = self.deref.build(context)
        if isinstance(subject, str):
            raise ValueError(f'TreeBuilder: [{self.label}] is bound to "{subject}".')
        return [self.content.build(context.put(self.label, item)) for item in subject]


