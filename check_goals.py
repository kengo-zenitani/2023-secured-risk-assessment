import os
import sys
from utils import load_attack_graph, fact_to_label

if len(sys.argv) < 2:
    print('arguments missing')
    exit(1)


goals = ('interrupted', 'leaked', 'productsSentToWrongPlace', 'moneySentToWrongAccount', 'accidentsOccur')

ag = load_attack_graph(sys.argv[1])


for goal in ag.filter_facts_with_pred(*goals):
    print(fact_to_label(goal))

# assets|customers|human_resources|materials|purchase_contracts|sales_contracts
# accounting_office|administration_office|customer_support_office|human_resource_office|production_office
