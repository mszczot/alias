class Subframework(object):
    def __init__(self, args: {}, attacks: list, id):
        self.__id = id
        self.__arguments = args
        self.__attacks = attacks
        self.__in = []
        self.__out = []
        self.__extension = []

    def __str__(self):
        return f'ID: {self.__id} \n Arguments: {self.__arguments} \n Attacks: {self.__attacks} \n In: {self.__in} \n ' \
               f'Out: {self.__out} \n Extensions: {self.__extension} '

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

    @property
    def extension(self):
        return self.__extension

    @extension.setter
    def extension(self, extension):
        self.__extension.append(extension)

    @in_edges.setter
    def in_edges(self, edges: list):
        self.__in = edges

    @out_edges.setter
    def out_edges(self, edges: list):
        self.__out = edges

    def add_attack(self, attacker: str, attacked: str):
        self.attacks.append((attacker, attacked))
