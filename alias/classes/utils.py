import networkx


def get_graph(args: dict, attacks):
    graph = networkx.nx.DiGraph()
    for n in args.keys():
        graph.add_node(n)
    for n in attacks:
        graph.add_edge(n[0], n[1])
    return graph
