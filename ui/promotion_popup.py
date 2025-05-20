from typing import Callable, Tuple

import pygame as pg

from constants import SQUARE_SIZE

from .image_button import ImageButton
from .piece_images import PIECE_IMAGES

from game.piece import Piece

class PromotionPopup:
    BG_COLOUR = pg.Color(255, 255, 255)
    
    def __init__(self, colour: int, pos: Tuple[int, int], on_promote: Callable[[int], int]) -> None:    
        self.__buttons = (
            ImageButton(PIECE_IMAGES[colour][Piece.QUEEN], (pos[0], pos[1]), on_promote, (Piece.QUEEN, )),
            ImageButton(PIECE_IMAGES[colour][Piece.ROOK], (pos[0], pos[1] + SQUARE_SIZE), on_promote, (Piece.ROOK, )),
            ImageButton(PIECE_IMAGES[colour][Piece.BISHOP], (pos[0], pos[1] + SQUARE_SIZE * 2), on_promote, (Piece.BISHOP, )),
            ImageButton(PIECE_IMAGES[colour][Piece.KNIGHT], (pos[0], pos[1] + SQUARE_SIZE * 3), on_promote, (Piece.KNIGHT, )),
        )
        self.__rect = pg.Rect(pos, (SQUARE_SIZE, SQUARE_SIZE * 4))
    
    def draw(self, win: pg.Surface) -> None:
        pg.draw.rect(win, PromotionPopup.BG_COLOUR, self.__rect, border_radius=9)
        
        for button in self.__buttons:
            button.draw(win)
            
    def poll(self, e: pg.Event) -> int | None:
        for button in self.__buttons:
            if button.poll(e):
                return button.invoke_callback()