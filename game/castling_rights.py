from enum import IntFlag

class CastlingRights(IntFlag):
    NONE = 0b0000
    WK = 0b0001
    WQ = 0b0010
    W = WK | WQ
    BK = 0b0100
    BQ = 0b1000
    B = BK | BQ
    ALL = W | B