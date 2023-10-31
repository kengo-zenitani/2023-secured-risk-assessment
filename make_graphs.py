import os
import sys
from utils import load_attack_graph

if len(sys.argv) < 2:
    print('arguments missing')
    exit(1)


ag = load_attack_graph(sys.argv[1])


with open(os.path.splitext(sys.argv[1])[0] + '.dot', 'w', encoding='utf-8') as graph:
    graph.write(ag.to_dot())
