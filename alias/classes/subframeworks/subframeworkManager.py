from collections import defaultdict

from alias.classes.subframeworks.subframework import Subframework
from alias.classes.subframeworks.tarjan import Tarjan
from alias.classes.utils import get_graph


class SubframeworkManager(object):
    def __init__(self):
        self.__subframeworks = {}
        self.__graph = None
        self.__mapping_args = {}
        self.__mapping_sub = defaultdict(list)
        self.__connected_components = []
        self.__generated = False

    def set_subframeworks(self, args: dict, attacks: list):
        self.__graph = get_graph(args, attacks)
        self.__generate_connected_components()
        self.__create_subframeworks(args)
        self.__generate_in_out_edges()
        self.__generated = True
        return self.__subframeworks

    def are_subframework_generated(self):
        return self.__generated

    def get_subframeworks(self):
        return self.__subframeworks

    def get_subframework(self, id: int):
        return self.__subframeworks[id]

    def get_root_subframeworks(self):
        root_subframework = []
        for framework in self.__subframeworks.values():
            if len(framework.in_edges) == 0:
                root_subframework.append(framework)
        return root_subframework

    def __create_subframeworks(self, args: dict):
        for component in self.__connected_components:
            index = len(self.__subframeworks)
            subgraph = self.__graph.subgraph(component)
            sub_args = {}
            for node in subgraph.nodes:
                sub_args[node] = args[node]
            self.__subframeworks[index] = Subframework(sub_args, [edge for edge in subgraph.edges], index)
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
                    in_edges.add(el)
            for el in self.__graph.out_edges(args):
                if el[1] not in set(args):
                    out_edges.add(el)
            component.in_edges = list(in_edges)
            component.out_edges = list(out_edges)

    def __get_rooted_frameworks(self):
        return [v for k, v in self.__subframeworks.items() if len(v.in_edges) == 0]

    def get_sub_framework_for_argument(self, argument: str):
        return self.get_subframework(self.__mapping_args[argument])
