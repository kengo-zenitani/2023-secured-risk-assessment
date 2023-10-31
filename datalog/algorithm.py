from collections import defaultdict
from collections.abc import Iterable
from functools import reduce
from typing import Any, Optional, Union

Atom = str


class Variable:
    def __init__(self, name: str):
        self.name = name

    def __hash__(self) -> int:
        return self.name.__hash__()

    def __eq__(self, another: Any) -> bool:
        return isinstance(another, Variable) and self.name == another.name

    def __repr__(self) -> str:
        return f'Variable(name={self.name})'


Predicate = str
Argument = Union[Atom, Variable]
Term = tuple[Predicate, Argument, ...]
Fact = tuple[Predicate, Atom, ...]
Rule = tuple[Term, ...]
Instance = tuple[Fact, ...]
LookupKey = tuple[Predicate, int, Atom]


def bind(terms: Iterable[Term], bindings: dict[Argument, Atom]) -> tuple[Term, ...]:
    return tuple((pred, *(bindings.get(arg, arg) for arg in args)) for pred, *args in terms)


def collate(term: Term, fact: Fact) -> Optional[dict[Argument, Atom]]:
    if all(arg == val or isinstance(arg, Variable) for arg, val in zip(term, fact)):
        return {arg: val for arg, val in zip(term, fact) if isinstance(arg, Variable)}
    else:
        return None


def lookup_keys(term: Term) -> Iterable[LookupKey]:
    pred, *args = term
    yield pred, -1, None
    for i, arg in enumerate(args):
        if not isinstance(arg, Variable):
            yield pred, i, arg


def unify(rule: Rule, keyed_facts: dict[LookupKey, set[Fact]]) -> Iterable[Instance]:

    def unify_terms(terms: Iterable[Term]) -> Iterable[tuple[Iterable[Term], dict[Argument, Atom]]]:
        head, *tail = terms
        if relevant_facts := [keyed_facts[lookup_key] for lookup_key in lookup_keys(head) if lookup_key in keyed_facts]:
            for fact in reduce(lambda a, b: a & b, relevant_facts):
                if (bindings := collate(head, fact)) is not None:
                    for unified_tail, tail_bindings in (unify_terms(bind(tail, bindings)) if tail else [([], {})]):
                        yield [head] + unified_tail, {**bindings, **tail_bindings}

    rule_head, *rule_body = rule
    for unified_body, body_bindings in unify_terms(rule_body):
        yield bind([rule_head] + unified_body, body_bindings)


def edge_rules(rules: set[Rule], edge_facts: set[Fact]) -> set[Rule]:
    return {bind(rule, bindings)
            for rule in rules
            for term in rule[1:] # terms in the body of the rule.
            for edge_fact in edge_facts
            if (bindings := collate(term, edge_fact)) is not None}


def process(rules: Iterable[Rule], facts: Iterable[Fact]) -> Iterable[Instance]:

    edge_facts = set(facts)
    keyed_facts: dict[LookupKey, set[Fact]] = defaultdict(set)
    for fact in facts:
        for lookup_key in lookup_keys(fact):
            keyed_facts[lookup_key].add(fact)

    while instances := {instance for rule in edge_rules(rules, edge_facts) for instance in unify(rule, keyed_facts)}:
        for instance in instances:
            yield instance

        edge_facts = set()
        for inferred_fact in {inferred_fact for inferred_fact, *_ in instances}:
            if inferred_fact not in keyed_facts[next(lookup_keys(inferred_fact))]:
                edge_facts.add(inferred_fact)
            for lookup_key in lookup_keys(inferred_fact):
                keyed_facts[lookup_key].add(inferred_fact)

