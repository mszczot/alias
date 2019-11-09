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
        self.__solver = Solver()
        self.__create_bool_variables(args)
        if extension is ExtensionType.CONFLICT_FREE:
            return self.__get_conflict_free_sets(attacks)
        if extension is ExtensionType.ADMISSIBLE:
            return self.__get_admissible_sets(args, attacks)
        if extension is ExtensionType.STAGE:
            return self.__get_stage_extension(args)
        if extension is ExtensionType.COMPLETE:
            return self.__get_complete_extensions(args, attacks)
        if extension is ExtensionType.PREFERRED:
            return self.__get_preferred_extensions(args, attacks)
        if extension is ExtensionType.STABLE:
            return self.__get_stable_extensions(args, attacks)

    def __get_conflict_free_sets(self, attacks: list):
        """
        Generates conflict free sets based on the attacks
        :param attacks: list of attacks in the argumentation framework
        :return:
        """
        self.__conflict_free_clauses(attacks)
        return self.__get_solutions()

    def __get_admissible_sets(self, args: dict, attacks: list):
        """
        Generates admissible sets based on arguments and attacks in the argumentation framework
        :param args: dictionary of arguments
        :param attacks: list of attacks in the argumentation framework
        :return:
        """
        self.__admissible_clauses(args, attacks)
        return self.__get_solutions()

    def __get_stage_extension(self, args: dict):
        """
        Generates the stage extension
        :param args: dictionary of arguments in the argumentation framework
        :return:
        """
        in_label = self.__get_root_args(args)
        out_label = []
        undec_label = [arg for arg in set(args.keys()) - set(in_label)]
        if len(in_label) == 0:
            return []

        finished = False
        while not finished:
            finished = True
            for arg in undec_label:
                for attacker in args[arg].attacked_by:
                    if attacker in in_label:
                        out_label.append(arg)
                        undec_label.remove(arg)
                        finished = False
                        break
            for arg in undec_label:
                all_out = True
                for attacker in args[arg].attacked_by:
                    if attacker not in out_label:
                        all_out = False
                        break
                if all_out:
                    in_label.append(arg)
                    undec_label.remove(arg)
                    finished = True

        return [arg for arg in in_label]

    def __get_complete_extensions(self, args: dict, attacks: list):
        self.__admissible_clauses(args, attacks)
        stage = self.__get_stage_extension(args)
        self.__solver.add(And([self.__variables[arg] for arg in stage]))
        return self.__get_solutions()

    def __get_preferred_extensions(self, args: dict, attacks: list):
        self.__admissible_clauses(args, attacks)
        stage = self.__get_stage_extension(args)
        self.__solver.add(And([self.__variables[arg] for arg in stage]))
        maximal = True
        return self.__get_solutions(maximal)

    def __get_stable_extensions(self, args: dict, attacks: list):
        self.__conflict_free_clauses(attacks)
        maximal = True
        possible_solutions = self.__get_solutions(maximal)
        solutions = []
        for solution in possible_solutions:
            attacked_args = set()
            for s in solution:
                for attacking in args[s].attacking:
                    attacked_args.add(attacking)
            if set(args.keys()) - set(solution) == attacked_args:
                solutions.append(solution)
        return solutions

    def __get_solutions(self, maximal: bool = False):
        """
        Method to iteratively get the solutions from the Z3 solver
        :return:
        """
        solutions = []
        prev_solution = []
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
            solution = [self.__mapping[arg] for arg in solution]
            if maximal:
                if set(prev_solution).issubset(set(solution)) and prev_solution in solutions:
                    solutions.remove(prev_solution)
                prev_solution = solution
            solutions.append(solution)
        return solutions

    @staticmethod
    def __get_root_args(args: dict):
        """
        Generates the list of rooted arguments
        :param args: dictionary of arguments in the argumentation framework
        :return:
        """
        my_return = []
        for arg in args.values():
            if not arg.is_attacked():
                my_return.append(arg.name)
        return my_return

    def __create_bool_variables(self, args: dict):
        """
        Maps the arguments of the argumentation framework into a dictionary of Boolean variables used by Z3
        :param args: dictionary of arguments in the argumentation framework
        :return:
        """
        self.__variables = {}
        self.__mapping = {}
        for k in args.keys():
            arg = Bool(k)
            self.__variables[k] = arg
            self.__mapping[arg] = k

    def __conflict_free_clauses(self, attacks: list):
        """
        Adds clauses for the conflict free sets
        :param attacks: list of attacks in the argumentation framework
        :return:
        """
        for attack in attacks:
            self.__solver.add(simplify(Implies((self.__variables[attack[0]]), Not(self.__variables[attack[1]]))))

    def __admissible_clauses(self, args: dict, attacks: list):
        """
        Adds clauses for the admissible sets
        :param args: a dictionary of arguments
        :param attacks: list of attacks in the argumentation framework
        :return:
        """
        self.__conflict_free_clauses(attacks)
        for k, arg in args.items():
            for attacker in arg.attacked_by:
                if args[attacker].is_attacked():
                    defenders = []
                    for defender in args[attacker].attacked_by:
                        if defender not in arg.attacked_by:
                            defenders.append(Implies(self.__variables[k], self.__variables[defender]))
                    if len(defenders) > 0:
                        self.__solver.add(Or(defenders))
                else:
                    self.__solver.add(Not(self.__variables[k]))

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
