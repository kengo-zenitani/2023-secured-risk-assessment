#!/bin/sh
echo "Analyzing Model-0..."
python3 ./datalog/datalog.py ./model-0.d
python3 ./make_graphs.py ./model-0.py
dot -Tsvg model-0.dot -o model-0.svg
python3 ./check_goals.py ./model-0.py
echo

echo "Analyzing Model-1..."
python3 ./datalog/datalog.py ./model-1.d
python3 ./make_graphs.py ./model-1.py
dot -Tsvg model-1.dot -o model-1.svg
python3 ./check_goals.py ./model-1.py
echo

echo "Analyzing Model-2..."
python3 ./datalog/datalog.py ./model-2.d
python3 ./make_graphs.py ./model-2.py
dot -Tsvg model-2.dot -o model-2.svg
python3 ./check_goals.py ./model-2.py
echo

echo "Done."
