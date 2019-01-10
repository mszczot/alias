from z3 import *

from alias.classes.solvers import BaseSolver, ExtensionType


class Z3Solver(BaseSolver):
    def __init__(self):
        super().__init__()
        self.__solver = Solver()
        self.__variables = dict()
        self.__mapping = dict()

    def solve(self, extension: ExtensionType, args: dict, attacks: list):
        self.__create_bool_variables(args)
        # if extension == ExtensionType.STAGE:
        root_args = self.__get_root_args(args)
        for x in root_args:
            self.__solver.add(And(self.__variables[x]))
        # self.__in_label_clause(args)
        self.__out_label_clause(args)
        self.__conflict_free_clause(attacks)
        solutions = []
        # print(self.__solver)
        while self.__solver.check() == sat:
            model = self.__solver.model()
            block = []
            solution = []
            for var in self.__variables.items():
                v = model.eval(var[1], model_completion=True)
                block.append(var[1] != v)
                if is_true(v):
                    solution.append(var[1])
            self.__solver.add(Or(block))
            test = []
            for i in solution:
                test.append(self.__mapping[i])
            solutions.append(test)
        return solutions

    @staticmethod
    def __get_root_args(args: dict):
        my_return = []
        for arg in args.values():
            if not arg.is_attacked():
                my_return.append(arg.name)
        return my_return

    def __create_bool_variables(self, args: dict):
        for k in args.keys():
            arg = Bool(k)
            self.__variables[k] = arg
            self.__mapping[arg] = k

    def __in_label_clause(self, args: dict):
        for k, a in args.items():
            if a.is_attacked():
                clause = []
                for att in a.attacked_by:
                    clause.append(And(self.__variables[att]))
                self.__solver.add(simplify(If(And(clause), Not(self.__variables[a.name]), And(self.__variables[a.name]))))

    def __out_label_clause(self, args: dict):
        for k, a in args.items():
            if a.is_attacked():
                clause = []
                for att in a.attacked_by:
                    clause.append(And(self.__variables[att]))
                self.__solver.add(simplify(If(Or(clause), Not(self.__variables[a.name]), And(self.__variables[a.name]))))

    def __conflict_free_clause(self, attacks: list):
        for attack in attacks:
            self.__solver.add(simplify(Or(Not(self.__variables[attack[0]]), Not(self.__variables[attack[1]]))))
