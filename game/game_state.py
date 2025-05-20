from enum import auto, Enum

class GameState(Enum):
    NONE = 0
    WAITING = auto()
    PLAYING = auto()
    GAME_OVER = auto()