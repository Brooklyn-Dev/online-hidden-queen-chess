import pygame as pg

class Board:
    SIZE = 600
    SQUARE_SIZE = SIZE // 8
    LIGHT_SQUARE = pg.Color(192, 192, 192)
    DARK_SQUARE = pg.Color(96, 96, 96)
    
    def __init__(self) -> None:
        self.x = 0
        self.y = 0
    
    def set_pos_centre(self, win: pg.Surface) -> None:
        self.x = (win.get_width() - Board.SIZE) // 2
        self.y = (win.get_height() - Board.SIZE) // 2

    def __draw_square(self, win: pg.Surface, file: int, rank: int) -> None:
        is_light_square = (file + rank) % 2 != 0
        colour = Board.LIGHT_SQUARE if is_light_square else Board.DARK_SQUARE
        x = self.x + file * Board.SQUARE_SIZE
        y = self.y + rank * Board.SQUARE_SIZE
        
        pg.draw.rect(win, colour, pg.Rect(x, y, Board.SQUARE_SIZE, Board.SQUARE_SIZE))  
        
    def draw(self, win: pg.Surface) -> None:     
        for file in range(8):
            for rank in range(8):
                self.__draw_square(win, file, rank)