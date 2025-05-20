from enum import auto, Enum

class GameResult(Enum):
    NONE = 0
    DISCONNECT = auto()
    CHECKMATE = auto()
    STALEMATE = auto()
    INSUFFICIENT_MATERIAL = auto()
    FIFTY_MOVE_RULE = auto()
    THREEFOLD_REPETITION = auto()