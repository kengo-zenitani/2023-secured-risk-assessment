import os
import sys
from typing import cast

from compiler import Interpreter, ProgramVisitor, compiler
from compiler.parser import ParsingFailed

from algorithm import process, Atom, Variable, Fact, Term, Predicate, Argument


class DatalogProcessor:
    def __init__(self):
        self.facts = set()
        self.rules = set()
        self.aggregations = {}

    def create_atom(self, name: str) -> Atom:
        return cast(Atom, name)

    def create_variable(self, name: str) -> Variable:
        return Variable(name=name)

    def create_term(self, predicate: str, args: list[Argument]) -> Term:
        return (predicate, *args)

    def register_fact(self, predicate: str, args: list[Atom]):
        self.facts.add((predicate, *args))

    def register_rule(self, head: Term, body: list[Term]):
        head_pred, *head_body = head
        head_variables = {arg for arg in head_body if isinstance(arg, Variable)}
        body_variables = {arg for _, *term_body in body for arg in term_body if isinstance(arg, Variable)}
        assert head_variables.issubset(body_variables)
        self.rules.add((head, *body))

    def register_aggregation(self, lhs: Atom, rhs: list[Atom]):
        for atom in rhs:
            assert atom not in self.aggregations
            self.aggregations[atom] = lhs

    def process(self):
        rules = self.rules
        facts = self.facts
        if self.aggregations:
            rules = {tuple((pred, *(self.aggregations.get(arg, arg) for arg in args)) for pred, *args in rule)
                     for rule in rules}
            facts = {(pred, *(self.aggregations.get(arg, arg) for arg in args)) for pred, *args in facts}

        return list(process(rules, facts))


class DatalogProgramVisitor(ProgramVisitor):
    def __init__(self, processor: DatalogProcessor):
        super().__init__()
        self.processor = processor

    def atom(self, attrs: dict[str, str], children: list[...]) -> Atom:
        return self.processor.create_atom(attrs['name'])

    def variable(self, attrs: dict[str, str], children: list[...]) -> Variable:
        return self.processor.create_variable(attrs['name'])

    def fact(self, attrs: dict[str, str], children: list[Atom]):
        self.processor.register_fact(attrs['predicate'], children)

    def head(self, attrs: dict[str, str], children: list[Term]):
        return children[0]

    def term(self, attrs: dict[str, str], children: list[Argument]) -> Term:
        return self.processor.create_term(attrs['predicate'], children)

    def rule(self, attrs: dict[str, str], children: list[Term, list[Term]]):
        head, body = children
        self.processor.register_rule(head, body)

    def aggregate(self, attrs: dict[str, str], children: list[Atom]) -> Term:
        self.processor.register_aggregation(attrs['to'], children)


app_dir = os.path.dirname(__file__)

with open(app_dir + '/datalog.g') as grammar:
    datalog_compiler = compiler(grammar.read())

if len(sys.argv) < 2:
    print('arguments missing')
    exit(1)

with open(sys.argv[1], encoding='utf-8') as program:
    compiled = datalog_compiler(program.read())
    processor = DatalogProcessor()
    Interpreter(DatalogProgramVisitor(processor)).interpret(compiled)

    with open(os.path.splitext(sys.argv[1])[0] + '.xml', 'w', encoding='utf-8') as parsed_xml:
        parsed_xml.write(compiled.toprettyxml())

    with open(os.path.splitext(sys.argv[1])[0] + '.py', 'w', encoding='utf-8') as data_py:
        data_py.write("[\n")
        for instance in processor.process():
            data_py.write(f"    {instance},\n")
        data_py.write("]\n")


