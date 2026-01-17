import json
import networkx as nx
import matplotlib.pyplot as plt

with open("output/workflow.json") as f:
    data = json.load(f)

G = nx.DiGraph()

for task in data["tasks"]:
    label = f"{task['id']}\n{task['assignee']}"
    G.add_node(task["id"], label=label)

for e in data["edges"]:
    G.add_edge(e[0], e[1])

pos = nx.spring_layout(G, seed=42)
labels = nx.get_node_attributes(G, "label")

nx.draw(G, pos, with_labels=False, node_size=3500)
nx.draw_networkx_labels(G, pos, labels)
plt.title("Meeting → Executable Workflow DAG")
plt.show()
