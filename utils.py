from collections import defaultdict
import hashlib
import os


class AttackGraph:
    @classmethod
    def from_instances(cls, instances):
        conditions = set()
        exploits = {}
        edges = set()
        for instance in instances:
            head, *body = instance
            conditions.add(head)
            exploit = hashlib.blake2b(str(instance).encode('utf-8')).hexdigest()
            if exploit not in exploits:
                exploits[exploit] = f"e{len(exploits) + 1}"
            for fact in body:
                conditions.add(fact)
                edges.add((fact, exploits[exploit]))
            edges.add((exploits[exploit], head))

        return cls(conditions, set(exploits.values()), edges)

    def __init__(self, conditions, exploits, edges):
        self.conditions = conditions
        self.exploits = exploits
        self.edges = edges

        self.dst_to_src = defaultdict(set)
        self.src_to_dst = defaultdict(set)
        for src, dst in edges:
            self.dst_to_src[dst].add(src)
            self.src_to_dst[src].add(dst)

    @property
    def initial_conditions(self):
        return self.conditions - {dst for src, dst in self.edges}

    def filter_facts_with_pred(self, *preds):
        goals = set()
        for condition in self.conditions:
            pred, *_ = condition
            if pred in preds:
                goals.add(condition)
        return goals

    def get_trace_tree(self, goals):

        traced_conditions = set()
        traced_exploits = set()
        traced_edges = set()

        def _trace_subgoals(goals):
            if goals:
                subgoals = set()
                traced_conditions.update(goals)
                for goal in goals:
                    for exploit in self.dst_to_src[goal]:
                        traced_edges.add((exploit, goal))
                        traced_exploits.add(exploit)
                        for condition in self.dst_to_src[exploit]:
                            traced_edges.add((condition, exploit))
                            subgoals.add(condition)
                _trace_subgoals(subgoals - traced_conditions)

        _trace_subgoals(goals)

        return AttackGraph(traced_conditions, traced_exploits, traced_edges)

    def get_formula(self, goals):
        # 経路表現式への変換(DAG化と同時に行う)
        assert 1 <= len(goals)

        uncontrollable_conditions = {c for c in self.initial_conditions if c[0] not in config.control_targets}
        uncontrollable_conditions.add(('noProtection', 'the_internet'))

        dst_to_src = self.dst_to_src.copy()
        backgrounds = defaultdict(set)

        def _expand_condition(condition, exploit):
            backgrounds[condition] |= {condition} | backgrounds[exploit]
            expanded = []
            for src in dst_to_src[condition]:
                if src not in backgrounds[condition]:
                    expanded_item = _expand_exploit(src, condition)
                    if expanded_item not in expanded:
                        expanded.append(expanded_item)
            if not expanded:
                return condition
            elif len(expanded) == 1:
                return expanded[0]
            else:
                return expanded

        def _expand_exploit(exploit, condition):
            backgrounds[exploit] |= {exploit} | backgrounds[condition]
            expanded = []
            for src in dst_to_src[exploit]:
                if src not in backgrounds[exploit] and src not in uncontrollable_conditions:
                    expanded_item = _expand_condition(src, exploit)
                    if expanded_item not in expanded:
                        expanded.append(expanded_item)
            expanded = tuple(c for c in expanded if c)
            return expanded[0] if len(expanded) == 1 else expanded

        if len(goals) == 1:
            return _expand_condition(list(goals)[0], None)
        else:
            dummy_exploit = 'ex'
            dst_to_src[dummy_exploit] = set(goals)
            return _expand_exploit(dummy_exploit, None)

    def to_dot(self) -> str:
        app_dir = os.path.dirname(__file__)
        with open(app_dir + '/graph_template.dot', 'r') as fp:
            template = fp.read()

        def node_to_label(node):
            return node if isinstance(node, str) else fact_to_label(node)

        sep = '_'
        node_defs = [f'"{node_to_label(condition)}" [shape=rect, style="rounded"];' for condition in self.conditions] + [f'"{exploit}" [shape=box];' for exploit in self.exploits]
        edge_defs = [f'"{node_to_label(src)}" -> "{node_to_label(dst)}";' for src, dst in self.edges]
        return template.replace('%Nodes%', '\n  '.join(node_defs)).replace('%Edges%', '\n  '.join(edge_defs))


def load_attack_graph(filename):
    with open(filename, encoding='utf-8') as datafile:
        return AttackGraph.from_instances(eval(datafile.read()))


def fact_to_label(fact):
    pred, *args = fact
    return f"{pred}({', '.join(args)})"


def isfact(term):
    return isinstance(term, tuple) and isinstance(term[0], str)


