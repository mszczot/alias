from collections import defaultdict

import networkx

from alias.classes.solvers.extensionType import ExtensionType
from alias.classes.solvers.solverManager import SolverManager
from alias.classes.subframeworks.subframework import Subframework
from alias.classes.subframeworks.tarjan import Tarjan


class SubframeworkManager(object):
    def __init__(self):
        self.__subframeworks = {}
        self.__graph = None
        self.__mapping_args = {}
        self.__mapping_sub = defaultdict(list)
        self.__connected_components = []
        self.__attacks = []
        self.__framework = {}
        self.__solverManager = SolverManager()

    def set_subframeworks(self, graph: networkx.DiGraph):
        self.__graph = graph
        self.__generate_connected_components()
        self.__create_subframeworks()
        self.__generate_in_out_edges()
        self.__framework['Arguments'] = list(self.__subframeworks.keys())
        self.__framework['Attacks'] = self.__attacks
        self.solve()
        return self.__subframeworks

    def __create_subframeworks(self):
        for component in self.__connected_components:
            index = len(self.__subframeworks)
            subgraph = self.__graph.subgraph(component)
            self.__subframeworks[index] = Subframework(subgraph.nodes, subgraph.edges, index)
            for c in component:
                self.__mapping_args[c] = index
                self.__mapping_sub[index].append(c)

    def __generate_connected_components(self):
        self.__connected_components = Tarjan(self.__graph.edges, self.__graph.nodes).tarjan()

    def __generate_in_out_edges(self):
        for k, component in self.__subframeworks.items():
            in_edges = set()
            out_edges = set()
            args = component.arguments
            for el in self.__graph.in_edges(args):
                if el[0] not in set(args):
                    in_edges.add(el[0])
            for el in self.__graph.out_edges(args):
                if el[1] not in set(args):
                    out_edges.add(el[1])
            component.in_edges = list(in_edges)
            component.out_edges = list(out_edges)
            self.__generate_attacks(component)

    def __generate_attacks(self, framework: Subframework):
        for el in framework.in_edges:
            self.__attacks.append((self.__mapping_args[el], framework.id))
        for el in framework.out_edges:
            self.__attacks.append((framework.id, self.__mapping_args[el]))

    def solve(self):
        rooted = self.__get_rooted_frameworks()
        for r in rooted:
            t = self.__solverManager.get_extension(ExtensionType.ADMISSIBLE, r.arguments, r.attacks, )
            print(t)

    def __get_rooted_frameworks(self):
        return [v for k, v in self.__subframeworks.items() if len(v.in_edges) == 0]
