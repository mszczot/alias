import numpy


class TestHelper(object):

    @staticmethod
    def read_solution_from_file(file):
        return list(list(line.split()) for line in open(file))

    @staticmethod
    def assert_lists_equal(expected, actual):
        expected_set = set([tuple(sorted(lst)) for lst in expected])
        actual_set = set([tuple(sorted(lst)) for lst in actual])

        error = 'Lists are not equal. Expected ' + str(expected_set) + ', actual: ' + str(actual_set) + '\n'
        error += 'Expected has ' + str(len(expected_set)) + ' items, Actual has ' + str(len(actual_set)) + ' items.'

        equal_length = len(expected_set & actual_set) is len(expected)
        if not equal_length:
            raise AssertionError(error)

        for expected in expected_set:
            if expected in actual_set:
                actual_set.remove(expected)
            else:
                raise AssertionError(error)
        if len(actual_set) > 0:
            raise AssertionError(error)
