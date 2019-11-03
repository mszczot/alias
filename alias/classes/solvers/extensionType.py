from enum import Enum


class ExtensionType(Enum):
    CONFLICT_FREE = 1
    ADMISSIBLE = 2
    COMPLETE = 3
    PREFERRED = 4
    STABLE = 5
    STAGE = 6
