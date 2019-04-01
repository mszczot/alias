class Tarjan(object):
    def __init__(self, edges: list, vertices: list):
        self.__edges = edges
        self.__vertices = vertices
        self.__indices = dict((v, -1) for v in self.__vertices)
        self.__lowlinks = self.__indices.copy()
        self.__connected_components = []

    def tarjan(self):
        index = 0
        stack = []
        for v in self.__vertices:
            if self.__indices[v] < 0:
                self.strong_connect(v, index, stack)
        return self.__connected_components

    def strong_connect(self, vertex, index, stack):
        self.__indices[vertex] = index
        self.__lowlinks[vertex] = index
        index += 1
        stack.append(vertex)

        for v, w in (e for e in self.__edges if e[0] == vertex):
            if self.__indices[w] < 0:
                self.strong_connect(w, index, stack)
                self.__lowlinks[v] = min(self.__lowlinks[v], self.__lowlinks[w])
            elif w in stack:
                self.__lowlinks[v] = min(self.__lowlinks[v], self.__indices[w])

        if self.__indices[vertex] == self.__lowlinks[vertex]:
            self.__connected_components.append([])
            while stack[-1] != vertex:
                self.__connected_components[-1].append(stack.pop())
            self.__connected_components[-1].append(stack.pop())

