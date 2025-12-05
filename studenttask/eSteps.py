from enum import Enum


class eSteps(Enum):
    """
    Enumeration representing possible tap changer control actions.

    Used to indicate whether the tap changer should move up, down or stay in current position.
    """

    # Move tap changer to lower position (decrease voltage)
    SWITCHLOWER: int = 0

    # Move tap changer to higher position (increase voltage)
    SWITCHHIGHER: int = 1

    # Keep tap changer in current position
    STAY: int = 2
