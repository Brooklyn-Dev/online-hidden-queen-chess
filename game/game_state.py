from enum import auto, Enum

class GameState(Enum):
    NONE = 0
    PLAYING = 2
    GAME_OVER = auto()