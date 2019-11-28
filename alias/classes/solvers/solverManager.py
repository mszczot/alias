from anytree import Node

from alias.classes.semantics.extensionManager import ExtensionManager
from alias.classes.matrix import Matrix
from alias.classes.solvers.extensionType import ExtensionType
from alias.classes.solvers.picosatSolver import PicosatSolver
from alias.classes.solvers.solverType import SolverType
from alias.classes.solvers.z3Solver import Z3Solver
from alias.classes.subframeworks.subframeworkManager import SubframeworkManager


class SolverManager(object):
    def __init__(self):
        self.solver = SolverType.Z3
        self.__extensions = {
            ExtensionType.CONFLICT_FREE: [],
            ExtensionType.ADMISSIBLE: [],
            ExtensionType.COMPLETE: [],
            ExtensionType.PREFERRED: [],
            ExtensionType.STABLE: [],
            ExtensionType.STAGE: []
        }
        self.dirty = False
        self.__extensionsManager = ExtensionManager()
        self.__subFrameworkManager = SubframeworkManager()

    def get_extensions(self, extension: ExtensionType, arguments: dict, attacks: list):
        if self.dirty or not self.__subFrameworkManager.are_subframework_generated():
            self.__subFrameworkManager.set_subframeworks(arguments, attacks)
        if self.dirty or len(self.__extensions[extension]) == 0:
            if self.dirty:
                self.__reset_extensions()
            solutions = self.__get_solver().solve(extension, arguments, attacks)
            self.dirty = False
            self.__extensions[extension] = solutions
        return self.__extensions[extension]

    def get_some_extension(self, extension: ExtensionType, arguments: dict, attacks: list, matrix: Matrix):
        if self.dirty or len(self.__extensions[extension]) == 0:
            if self.dirty:
                self.__reset_extensions()
            possible_solutions = self.__get_solver().solve(extension, arguments, attacks)
            for solution in next(possible_solutions):
                if self.__extensionsManager.extensions[extension].verify_solution(solution, arguments, matrix):
                    return solution
        else:
            return self.__extensions[extension][0]

    def is_credulously_accepted(self, extension: ExtensionType, arguments: dict, attacks: list, argument, matrix: Matrix):
        if self.dirty or len(self.__extensions[extension]) == 0:
            if self.dirty:
                self.__reset_extensions()
            possible_solutions = self.__get_solver().solve(extension, arguments, attacks)
            for solution in next(possible_solutions):
                if self.__extensionsManager.extensions[extension].verify_solution(solution, arguments, matrix):
                    if argument in solution:
                        return True
        else:
            for solution in self.__extensions[extension]:
                if argument in solution:
                    return True
        return False

    def is_skeptically_accepted(self, extension: ExtensionType, arguments: dict, attacks: list, argument, matrix: Matrix):
        if self.dirty or len(self.__extensions[extension]) == 0:
            if self.dirty:
                self.__reset_extensions()
                self.dirty = False
            possible_solutions = self.__get_solver().solve(extension, arguments, attacks)
            for solution in next(possible_solutions):
                if self.__extensionsManager.extensions[extension].verify_solution(solution, arguments, matrix):
                    if argument not in solution:
                        return False
        else:
            for solution in self.__extensions[extension]:
                if argument not in solution:
                    return False
        return True

    def __get_solver(self):
        if self.solver == SolverType.PICOSAT:
            return PicosatSolver()
        elif self.solver == SolverType.Z3:
            return Z3Solver()

    def __reset_extensions(self):
        for k in self.__extensions:
            self.__extensions[k] = []

    def __get_rooted_solutions(self, extension):
        rooted_sub_frameworks = self.__subFrameworkManager.get_root_subframeworks()
        rooted_solutions = []
        if len(rooted_sub_frameworks) > 0:
            for rooted in rooted_sub_frameworks:
                rooted_solutions = self.__generate_possible_solutions(extension, rooted, rooted_solutions)
        return rooted_solutions

    def __generate_possible_solutions(self, extension, framework, solutions):
        possible_solutions = self.__get_solver().solve(extension, framework.arguments, framework.attacks)
        if len(possible_solutions) == 0:
            return solutions
        elif len(possible_solutions) == 1 and possible_solutions[0] not in solutions and possible_solutions[0] != []:
            for solution in solutions:
                if not any(x in solution for x in framework.in_edges):
                    solutions.remove(solution)
                    solution = solution + possible_solutions[0]
                    solutions.append(solution)
        elif len(possible_solutions) > 1:
            temp = []
            for solution in possible_solutions:
                if len(solutions) > 0:
                    for rooted_solution in solutions:
                        temp.append(rooted_solution + solution)
                else:
                    temp.append(solution)
            solutions = temp
        return solutions

    def __build_solutions(self, current_sub_framework, solutions, extension):
        my_solutions = solutions.copy()
        sub_frameworks = self.__get_next_sub_framework(current_sub_framework)
        if len(sub_frameworks) == 0:
            return my_solutions

        for framework in sub_frameworks:
            entry_points = {element[0]: True for element in framework.in_edges}
            for entry_point in entry_points:
                if not all(entry_point in solution for solution in my_solutions):
                    entry_points[entry_point] = False
                else:
                    attacked = [x[1] for x in framework.in_edges if entry_point == x[0]]
                    framework.add_attack(attacked[0], attacked[0])
            self.__generate_possible_solutions(extension, framework, my_solutions)

        my_solutions = self.__build_solutions(sub_frameworks, my_solutions, extension)
        return my_solutions

    def __get_next_sub_framework(self, current_sub_frameworks: list):
        sub_frameworks = []
        for sub_framework in current_sub_frameworks:
            if len(sub_framework.out_edges) > 0:
                for element in sub_framework.out_edges:
                    sub_frameworks.append(self.__subFrameworkManager.get_sub_framework_for_argument(element[1]))
        return sub_frameworks
