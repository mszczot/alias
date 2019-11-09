import numpy


class TestHelper(object):

    @staticmethod
    def read_solution_from_file(file):
        return list(list(line.split()) for line in open(file))

    @staticmethod
    def assert_lists_equal(expected, actual):
        expected_set = set([tuple(sorted(lst)) for lst in expected])
        actual_set = set([tuple(sorted(lst)) for lst in actual])
        equal_length = len(expected_set & actual_set) is len(expected)
        if not equal_length:
            error = 'Lists are not equal. Expected ' + str(expected) + ', actual: ' + str(actual) + '\n'
            error += 'Expected has ' + str(len(expected)) + ' items, Actual has ' + str(len(actual)) + ' items.'
            raise AssertionError(error)

        expected_numpy = numpy.array([numpy.array(sorted(x)) for x in expected])
        actual_numpy = numpy.array([numpy.array(sorted(x)) for x in actual])
        if not numpy.array_equal(expected_numpy, actual_numpy):
            error = 'Lists are not equal. Expected ' + str(expected) + ', actual: ' + str(actual) + '\n'
            error += 'Expected has ' + str(len(expected)) + ' items, Actual has ' + str(len(actual)) + ' items.'
            raise AssertionError(error)
