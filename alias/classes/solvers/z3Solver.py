from z3 import *
from tarjan.tc import tc

from alias.classes.solvers import BaseSolver, ExtensionType


class Z3Solver(BaseSolver):
    def __init__(self):
        super().__init__()
        self.__solver = Solver()
        self.__variables = dict()
        self.__mapping = dict()

    def solve(self, extension: ExtensionType, args: dict, attacks: list):
        return self.test(args, attacks)

    def test(self, args, attacks):
        self.__solver = Solver()
        self.__create_bool_variables(args)
        root_args = self.__get_root_args(args)
        for x in root_args:
            self.__solver.add(And(self.__variables[x]))
        # if extension == ExtensionType.STAGE:
        self.__in_label_clause(args)
        self.__out_label_clause(args)
        # self.__conflict_free_clause(attacks)
        # self.__get_defence_arguments(args)
        solutions_set = set()
        # print(self.__solver)
        solutions = self.__get_solutions()
        my_result = set()
        for sol in solutions:
            solutions_set.add(frozenset(sol))
            my_result.add(frozenset(sol))
        for sol_set in solutions_set:
            for ss in solutions_set:
                if ss is not sol_set and sol_set.issubset(ss):
                    try:
                        my_result.remove(sol_set)
                    except:
                        continue
        return [list(x) for x in my_result]

    def __get_solutions(self):
        solutions = []
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
        self.__variables = {}
        self.__mapping = {}
        for k in args.keys():
            arg = Bool(k)
            self.__variables[k] = arg
            self.__mapping[arg] = k

    def __in_label_clause(self, args: dict):
        for k, a in args.items():
            elements = []
            for attacker in a.attacked_by:
                if attacker in self.__variables:
                    elements.append(self.__variables[attacker])
            if a.is_attacked():
                self.__solver.add(simplify(Implies(Not(And(elements)), self.__variables[a.name])))
                # self.__solver.add(If(And(elements), Not(self.__variables[a.name]), And(self.__variables[a.name])))

    def __out_label_clause(self, args: dict):
        for k, a in args.items():
            if a.is_attacked():
                elements = []
                for attacker in a.attacked_by:
                    if attacker in self.__variables:
                        elements = self.__variables[attacker]
                self.__solver.add(simplify(Implies(Or(elements), Not(self.__variables[a.name]))))
                # self.__solver.add(If(Or(elements), Not(self.__variables[a.name]), And(self.__variables[a.name])))

    def __conflict_free_clause(self, attacks: list):
        for attack in attacks:
            self.__solver.add(simplify(Or(Not(self.__variables[attack[0]]), Not(self.__variables[attack[1]]))))

    def __get_max_conflict_free(self, attacks: list):
        for attack in attacks:
            self.__solver.add(simplify(Or(Not(self.__variables[attack[0]]), Not(self.__variables[attack[1]]))))
        solutions = []
        self.get_models(self.__solver)
        print(self.__solver)

        return solutions

    def __is_max(self, solutions):
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

    def get_models(self, s):
        result = []
        while self.__solver.check() == sat:
            m = s.model()
            result.append(m)
            # Create a new constraint the blocks the current model
            block = []
            for d in m:
                # d is a declaration
                if d.arity() > 0:
                    raise Z3Exception("uninterpreted functions are not supported")
                # create a constant from declaration
                c = d()
                if is_array(c) or c.sort().kind() == Z3_UNINTERPRETED_SORT:
                    raise Z3Exception("arrays and uninterpreted sorts are not supported")
                block.append(c != m[d])
            s.add(Or(block))
        return result

    def __get_defence_arguments(self, args: dict):
        for k, v in args.items():
            if v.is_attacked():
                for att in v.attacked_by:
                    if args[att].is_attacked():
                        for defender in args[att].attacked_by:
                            def_arg = args[defender]
                            if v.name not in def_arg.attacking:
                                self.__solver.add(
                                    simplify(Implies(self.__variables[v.name], self.__variables[def_arg.name])))

    def get_subframeworks(self, args):
        a = {}
        for k, arg in args.items():
            a[arg.name] = arg.attacking
        test = tc(a)
        result = set()
        for k, v in test.items():
            subset = False
            if len(v) > 0:
                # v = set(v)
                # v.add(k)
                if v not in result:
                    for i, r in test.items():
                        if set(v) != set(r) and set(v).issubset(r):
                            subset = True
                    if not subset:
                        result.add(frozenset(v))
        return result
