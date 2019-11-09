from alias.classes.semantics.extensionManager import ExtensionManager
from alias.classes.matrix import Matrix
from alias.classes.solvers.extensionType import ExtensionType
from alias.classes.solvers.picosatSolver import PicosatSolver
from alias.classes.solvers.solverType import SolverType
from alias.classes.solvers.z3Solver import Z3Solver


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

    def get_extension(self, extension: ExtensionType, arguments: dict, attacks: list):
        if self.dirty or len(self.__extensions[extension]) == 0:
            if self.dirty:
                self.__reset_extensions()
                self.dirty = False
            possible_solutions = self.__get_solver().solve(extension, arguments, attacks)
            self.__extensions[extension] = possible_solutions if possible_solutions else []
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
