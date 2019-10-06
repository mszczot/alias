class Subframework(object):
    def __init__(self, args: list, attacks: list, id):
        self.__id = id
        self.__arguments = args
        self.__attacks = attacks
        self.__in = []
        self.__out = []

    def __str__(self):
        return 'ID: {} \n Arguments: {} \n Attacks: {} \n In: {} \n Out: {}'.format(self.__id, self.__arguments, self.__attacks, self.__in, self.__out)

    @property
    def id(self):
        return self.__id

    @property
    def arguments(self):
        return self.__arguments

    @property
    def attacks(self):
        return self.__attacks

    @property
    def in_edges(self):
        return self.__in

    @property
    def out_edges(self):
        return self.__out

    @in_edges.setter
    def in_edges(self, edges: list):
        self.__in = edges

    @out_edges.setter
    def out_edges(self, edges: list):
        self.__out = edges
