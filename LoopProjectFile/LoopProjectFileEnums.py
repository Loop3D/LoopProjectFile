import enum


class EventType(enum.IntEnum):
    INVALIDEVENT = (-1,)
    FAULTEVENT = (0,)
    FOLDEVENT = (1,)
    FOLIATIONSEVENT = (2,)
    DISCONTINUITYEVENT = (3,)
    STRATIGRAPHICLAYER = 4


class EventRelationshipType(enum.IntEnum):
    INVALIDTYPE = -1
    STRATA_STRATA = 0
    FAULT_STRATA = 1
    FAULT_FAULT_SPLAY = 2
    FAULT_FAULT_ABUT = 3
    FAULT_FAULT_OVERPRINT = 4


class ThicknessCalculatorType(enum.IntEnum):
    ALPHA = 0
    INTERPOLATED_STRUCTURE = 1
    STRUCTURAL_POINT = 2
    PLACEHOLDER_1 = 3
    PLACEHOLDER_2 = 4
