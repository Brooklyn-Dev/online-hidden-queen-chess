from dataclasses import dataclass, field
import json
import socket
from typing import List

from game.board import Board

@dataclass
class GameRoom:
    room_id: int
    players: List[socket.socket] = field(default_factory=list)
    board: Board = field(default_factory=Board)