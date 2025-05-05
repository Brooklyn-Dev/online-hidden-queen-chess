import sys

import pygame as pg

import game

WIN_SIZE = (800, 800)
BG_COLOUR = pg.Color(48, 48, 48)
FPS = 60

def main() -> None:
    pg.init()
    win = pg.display.set_mode(WIN_SIZE)
    pg.display.set_caption("Online Hidden Queen Chess")
    clock = pg.time.Clock()
    
    board = game.Board()
    board.set_pos_centre(win)
        
    while True:
        clock.tick(FPS)
        
        win.fill(BG_COLOUR)
        board.draw(win)
        
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                sys.exit(0)
                
            board.handle_pg_event(e)
                
        pg.display.flip()

if __name__ == "__main__":
    main()