from os import path
from typing import Dict

import pygame as pg

from constants import SQUARE_SIZE

from game.piece import Piece

PIECE_IMAGES: Dict[int, Dict[int, pg.Surface]] = {
    Piece.WHITE: {},
    Piece.BLACK: {}
}

for colour, prefix in ((Piece.WHITE, "w"), (Piece.BLACK, "b")):
    for piece_type, suffix in (
        (Piece.PAWN, "p"),
        (Piece.KING, "k"),
        (Piece.KNIGHT, "n"),
        (Piece.BISHOP, "b"),
        (Piece.ROOK, "r"),
        (Piece.QUEEN, "q")
    ):
        image = pg.image.load(path.join("image", f"{prefix}{suffix}.png"))
        scaled = pg.transform.smoothscale(image, (SQUARE_SIZE, SQUARE_SIZE))
        PIECE_IMAGES[colour][piece_type] = scaled