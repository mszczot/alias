class TestHelper(object):

    @staticmethod
    def read_solution_from_file(file):
        return list(list(line.split()) for line in open(file))

    @staticmethod
    def assert_lists_equal(expected, actual):
        expected = [frozenset(x) for x in expected]
        actual = [frozenset(x) for x in actual]
        equal = len(set(actual) - set(expected)) == 0
        if not equal:
            error = 'Lists are not equal. Expected ' + str(expected) + ', actual: ' + str(actual) + '\n'

            error += '\nExpected has ' + str(len(expected)) + ' items, Actual has ' + str(len(actual)) + ' items.'
            raise AssertionError(error)

